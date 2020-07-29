import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
from app import app

import math
import numpy as np
import pandas as pd
import plotly.offline as pyo
import plotly.express as px
import plotly.graph_objs as go
import dash as dash


from datetime import datetime as dt
from datetime import timedelta
import re
import multiprocessing as mp

import json
import requests
import util as util
from elasticsearch import Elasticsearch
from elasticsearch import helpers
from time import sleep


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

def gen_cmd_to_switch_by_dates(switchId, startDate, endDate):
    mapping = {'Left': 1, 'Right': 2}
    

    #df = gen_switch_data_df(switchId, startDate, endDate)
    data = pd.DataFrame()
    while startDate < endDate:
        end = startDate + timedelta(days=1)
        start_, end_  = util.date2str2(startDate, end)
        df = get_switch_data(switchId, start_, end_)
        if df is not None:
            if df.empty == False:
                df = df.replace({'positionDesc': mapping})
                data = data.append(getcmd_switch_times(df))
            else:
                sleep(0.1)    
        else:
            sleep(0.1)
            
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

# def gen_cmd_to_switch_by_dates(switchId, startDate, endDate):
#     mapping = {'Left': 1, 'Right': 2}
    

#     df = gen_switch_data_df(switchId, startDate, endDate)
#     if df is not None:
#         if df.empty == False:
#             df = df.replace({'positionDesc': mapping})
#             df = getcmd_switch_times(df)
#             df["switchId"] = switchId
#             return df


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

def add_fails(x):
    if x > 30:
        return 1
    else:
        return 0 

def upload_ELsearch(switchId, startDate, endDate):
    df = gen_cmd_to_switch_by_dates(switchId, startDate, endDate)
    print(switchId)
    if df is None:
        return
    if df.empty == False:
        df = df.set_index("loggedAt")
        df["fail"] = df.apply(lambda row: add_fails(row["moved_t"]), axis=1)
        # df = df.sort_index()
        # df["move_t_max_15min"] = df["moved_t"].rolling('15T').max()
        # df["self_move_sum_15min"] = df["self_move_amt"].rolling('15T').sum()
        # df["move_t_max_30min"] = df["moved_t"].rolling('30T').max()
        # df["self_move_sum_30min"] = df["self_move_amt"].rolling('30T').sum()
        # df["move_t_max_45min"] = df["moved_t"].rolling('45T').max()
        # df["self_move_sum_45min"] = df["self_move_amt"].rolling('45T').sum()
        # df["move_t_max_1H"] = df["moved_t"].rolling('1H').max()
        # df["self_move_sum_1H"] = df["self_move_amt"].rolling('1H').sum()
        df = df.between_time("6:00", "00:00")
        df = df.reset_index()
        
        df["loggedAt"] = df["loggedAt"].apply(lambda x: x.isoformat())
        insertDataframeIntoElastic(df, "self_move_delay")
    
    
    


if __name__ == "__main__":
    start_date = dt(2014, 1, 1)
    end_date = dt(2015, 8, 24)
    switches = get_switchId(start_date, end_date)
    df = pd.DataFrame()

    
    # df = gen_cmd_to_switch_by_dates(101, start_date, end_date)
    # df
    #upload_ELsearch(101, start_date, end_date)
    pool = mp.Pool(9)

    
    df.append(pool.starmap(upload_ELsearch, [(i, start_date, end_date) for i in switches]))

    pool.close()
    #insertDataframeIntoElastic(df, "cmd_to_switch")



# def getcmd_switch_times(df):
#     val = 0
#     val_1 = 0
#     loggedAt= []
#     moved_t = []
#     cont = True

#     prev = 0
#     date = df["loggedAt"].min() 
#     d_amt = []
#     d_date = []
    
#     for ind in df.index:
#         if df['switchCommand'][ind] != 0: 
#             val = df['switchCommand'][ind]
#             t1 = df['loggedAt'][ind]
#             cont = True
#         if val == df['positionDesc'][ind] and cont == True:
#             loggedAt.append(t1)
#             t2 = df['loggedAt'][ind] - t1
#             t2 = t2.total_seconds()
#             moved_t.append(t2)
#             cont = False
#         if val_1 == df['switchCommand'][ind]:
#             d_date.append(date)
#             d_amt.append(ind - prev)
#             val = 0
#             prev = ind
#             date = df['loggedAt'][ind]
            
#     data = pd.DataFrame(d_date,columns =['loggedAt'])
#     data["self_move_amt"] = d_amt
#     data["self_move_amt"] = data["self_move_amt"] - 3
    
#     data = pd.DataFrame(loggedAt,columns =['loggedAt'])
#     data["moved_t"] = moved_t
#     return data

#def gen_switching_counts(df):    
#     prev = 0
#     date = df["loggedAt"].min() 
#     val = 0
#     d_amt = []
#     d_date = []
#     for ind in df.index:
#         if val == df['switchCommand'][ind]:
#             pass
#         else:
#             d_date.append(date)
#             d_amt.append(ind - prev)
#             val = 0
#             prev = ind
#             date = df['loggedAt'][ind]
#     data = pd.DataFrame(d_date,columns =['loggedAt'])
#     data["self_move_amt"] = d_amt
#     data["self_move_amt"] = data["self_move_amt"] - 3
#     # indexNames = data[ data['self_move_amt'] <= 3 ].index
#     # data.drop(indexNames , inplace=True)
#     return data

# def gen_cmd_to_switch_by_dates(switchId, startDate, endDate):
#     mapping = {'Left': 1, 'Right': 2}
#     data1 = pd.DataFrame()
#     data2 = pd.DataFrame()

#     df = gen_switch_data_df(switchId, startDate, endDate)
#     if df is not None:
#         if df.empty == False:
#             data2 = gen_switching_counts(df)
#             df = df.replace({'positionDesc': mapping})
#             data1 = getcmd_switch_times(df)
#             data1 = data1.set_index('loggedAt').tz_localize(None)
#             data2 = data2.set_index('loggedAt').tz_localize(None)

#             df = data1.join(data2, how='outer')
#             df = df.fillna(value = 0)
#             df["switchId"] = switchId
#             return df

# def gen_switch_data_df(switchId, startDate, endDate):
#     data = pd.DataFrame()
#     while startDate < endDate:
#         end = startDate + timedelta(days=2)
#         start_, end_  = util.date2str2(startDate, end)
#         df = get_switch_data(switchId, start_, end_)
#         data = data.append(df)
#         startDate = end
#     return data


# def gen_cmd_to_switch_by_dates(switchId, startDate, endDate):
#     mapping = {'Left': 1, 'Right': 2}
#     df = pd.DataFrame()
#     #start_, end_  = util.date2str2(startDate, endDate)
#     data = gen_switch_data_df(switchId, startDate, endDate)
#     data = data.replace({'positionDesc': mapping})
#     while startDate < endDate:
#         end = startDate + timedelta(days=1)
#         #d = data[(startDate < data["loggedAt"])&(data["loggedAt"] <= end)] 
#         d = data.loc[startDate : end]
#         if d is not None:
#             if d.empty == False:
#                 d = d.reset_index()
#                 d = getcmd_switch_times(d)
#                 df = df.append(d)
#                 startDate = end
    
#     df["switchId"] = switchId
#     return df