import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State

import math
import numpy as np
import pandas as pd
import plotly.offline as pyo
import plotly.express as px
import plotly.graph_objs as go
import dash as dash


from datetime import datetime as dt
from dateutil.relativedelta import relativedelta, MO
from datetime import timedelta
import re
import multiprocessing as mp
from multiprocessing import Lock
from multiprocessing import Process

import json
import requests
import util as util
from elasticsearch import Elasticsearch
from elasticsearch import helpers
from time import sleep

def get_trainId(start_date, end_date):
    start_date, end_date  = util.date2str2(start_date, end_date )
    query = ("SELECT vobcid from dlr_train_move where loggedAt >= '{}' and loggedAt < '{}' "
    " group by vobcid").format(start_date, end_date)
    L = util.run_query(query)
    L = L["vobcid"].tolist()
    return L

def get_operating_hours_by_month(start_date, end_date, trainId):
    query = (" SELECT HISTOGRAM(loggedAt, INTERVAL 1 hour) as h, vobcid from dlr_train_move"
    "  where loggedAt >= '{}' and loggedAt < '{}' and vobcid ={} group by vobcid, h").format(start_date, end_date, trainId)
    L = util.run_query(query)
    return len(L.index)

def get_op_hours(startDate, endDate, trainId):
    month = []
    hours = []
    while startDate < endDate:
        end = startDate + relativedelta(months=+1)
        start_, end_  = util.date2str2(startDate, end)
        # l.acquire()
        # try:
        #     df = get_operating_hours_by_month(start_, end_, trainId)
        # finally:
        #     l.release()
        df = get_operating_hours_by_month(start_, end_, trainId)
        hours.append(df)
        month.append(startDate)
        startDate = end
    d = {"loggedMonth": month, "op_time": hours}
    df = pd.DataFrame(data = d)
    df["vobcid"] = trainId
    return df    

def get_switchId(start_date, end_date):
    start_date, end_date  = util.date2str2(start_date, end_date )
    query = ("SELECT switchId from dlr_switch_move where loggedAt >= '{}' and loggedAt < '{}' "
    " group by switchId").format(start_date, end_date)
    L = util.run_query(query)
    L = L["switchId"].tolist()
    return L


def getcmd_switch_times(df):
    val = 0
    val_1 = 0
    loggedAt= []
    moved_t = []
    d_amt = []
    cont = True

    prev = 0
    date = df["loggedAt"].min() 
    
    
    for ind in df.index:
        if df['switchCommand'][ind] != 0: 
            val = df['switchCommand'][ind]
            t1 = df['loggedAt'][ind]
            cont = True
        if val == df['positionDesc'][ind] and cont == True:
            loggedAt.append(t1)
            t2 = df['loggedAt'][ind] - t1
            t2 = t2.total_seconds()
            moved_t.append(t2)
            d_amt.append(0)
            cont = False
        if val_1 != df['switchCommand'][ind]:
            loggedAt.append(date)
            x = ind - prev
            if x <= 3:
                d_amt.append(0)
            else: 
                d_amt.append(x-3)
            moved_t.append(0)
            val_1 = df['switchCommand'][ind]
            prev = ind
            date = df['loggedAt'][ind]

    data = pd.DataFrame(loggedAt,columns =['loggedAt'])        
    data["self_move_amt"] = d_amt
    data["moved_t"] = moved_t
    data.drop(data.tail(3).index,inplace=True)
    return data


def get_switch_data(switchId, start_date, end_date):
    query = ("SELECT switchCommand, switchCommandDesc,statusDesc,positionDesc, loggedAt, switchId from dlr_switch_move"
    " where switchId = {} and loggedAt >= '{}' and loggedAt < '{}'"
    " order by loggedAt ").format(switchId, start_date, end_date)
    df = util.run_query(query)
    if df.empty == True:
        return 
    df = df.set_index("loggedAt")
    df = df.between_time("6:00", "00:00")
    df = df.reset_index()
    return df

def gen_cmd_to_switch_by_dates(switchId, startDate, endDate, l):
    mapping = {'Left': 1, 'Right': 2}
    data = pd.DataFrame()
    while startDate < endDate:
        end = startDate + timedelta(days=2)
        start_, end_  = util.date2str2(startDate, end)
        l.acquire()
        try:
            df = get_switch_data(switchId, start_, end_)
        finally:
            l.release()
        #df = get_switch_data(switchId, start_, end_)
        if df is not None:
            if df.empty == False:
                df = df.replace({'positionDesc': mapping})
                data = data.append(getcmd_switch_times(df))
            
        startDate = end
    data["switchId"] = switchId
    return data

# def gen_switch_data_df(switchId, startDate, endDate):
#     data = pd.DataFrame()
#     while startDate < endDate:
#         end = startDate + timedelta(days=2)
#         start_, end_  = util.date2str2(startDate, end)
#         df = get_switch_data(switchId, start_, end_)
#         data = data.append(df, ignore_index = True)
#         startDate = end
#     return data

# def gen_cmd_to_switch_by_dates(switchId, startDate, endDate , l):
#     mapping = {'Left': 1, 'Right': 2}
    
#     l.acquire()         
#     try:             
#         df = gen_switch_data_df(switchId, startDate, endDate)        
#     finally:
#         l.release()
    
#     if df is not None:
#         if df.empty == False:
#             df = df.replace({'positionDesc': mapping})
#             df = getcmd_switch_times(df)
#             df["switchId"] = switchId
#             return df


def add_fails(x):
    if x > 30:
        return 1
    else:
        return 0 


def insertDataframeIntoElastic(dataFrame,index='index', typ = 'test', server = 'http://localhost:9200',
                           chunk_size = 2500):
    headers = {'content-type': 'application/x-ndjson', 'Accept-Charset': 'UTF-8'}
    records = dataFrame.to_dict(orient='records')
    actions = ["""{ "index" : { "_index" : "%s", "_type" : "%s"} }\n""" % (index, typ) +json.dumps(records[j])
                    for j in range(len(records))]
    i=0
    while i<len(actions):
        serverAPI = server + '/_bulk' 
        data='\n'.join(actions[i:min([i+chunk_size,len(actions)])])
        data = data + '\n'
        requests.post(serverAPI, data = data, headers=headers)
        #print (r.content)
        i = i+chunk_size

# def upload_ELsearch(trainId_list, startDate, endDate,lock):
#     for trainId in trainId_list:
#         df = get_op_hours(startDate, endDate, trainId,lock)
#         df["loggedMonth"] = df["loggedMonth"].apply(lambda x: x.isoformat())
#         insertDataframeIntoElastic(df,index='op_hours')
#         print(trainId)
def upload_ELsearch(trainId, startDate, endDate):
    df = get_op_hours(startDate, endDate, trainId)
    df["loggedMonth"] = df["loggedMonth"].apply(lambda x: x.isoformat())
    insertDataframeIntoElastic(df,index='op_hours')
    print(trainId) 

def upload_ELsearch_smd(switchId_List, startDate, endDate, lock):
    for switchId in switchId_List:
        df = gen_cmd_to_switch_by_dates(switchId, startDate, endDate, lock)
        if df is None:
            return
        if df.empty == False:
            df = df.set_index("loggedAt")
            df["fail"] = df.apply(lambda row: add_fails(row["moved_t"]), axis=1)
            df = df.between_time("6:00", "00:00")
            df = df.reset_index()
            df["loggedAt"] = df["loggedAt"].apply(lambda x: x.isoformat())
            insertDataframeIntoElastic(df, "self_move_delay")
            print(switchId)
        
def chunker_list(seq, size):
    return (seq[i::size] for i in range(size))


if __name__ == "__main__":
    start_date = dt(2014, 1, 1)
    end_date = dt(2015, 8, 24)
    lock = Lock()
    switches = get_switchId(start_date, end_date)
    trains = get_trainId(start_date, end_date)
    processes = 6
   
    #tr = chunker_list(trains, processes)
    sw = chunker_list(switches, processes)

    # for i in tr:
    #     Process(target=upload_ELsearch_smd, args=(i, start_date, end_date, lock)).start()

    pool = mp.Pool(4)
    pool.starmap(upload_ELsearch, [(i, start_date, end_date) for i in trains])
    pool.close()

    for i in sw:
        Process(target=upload_ELsearch_smd, args=(i, start_date, end_date, lock)).start()
    

    # pool = mp.Pool(2)
    # pool.starmap(upload_ELsearch, [(i, start_date, end_date) for i in trains])
    # pool.close()

    #pool.starmap(upload_ELsearch_smd, [(i, start_date, end_date, lock) for i in switches])
    # for num in switches:
    #     Process(target=f, args=(lock, num)).start()