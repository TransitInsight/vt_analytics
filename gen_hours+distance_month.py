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
        df = get_operating_hours_by_month(start_, end_, trainId)
        hours.append(df)
        month.append(startDate)
        startDate = end
    d = {"loggedMonth": month, "op_time": hours}
    df = pd.DataFrame(data = d)
    df["vobcid"] = trainId
    return df    

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

def upload_ELsearch(trainId, startDate, endDate):
    df = get_op_hours(startDate, endDate, trainId)
    df["loggedMonth"] = df["loggedMonth"].apply(lambda x: x.isoformat())
    insertDataframeIntoElastic(df,index='op_hours')
    print(trainId)


    
    


if __name__ == "__main__":
    start_date = dt(2014, 1, 1)
    end_date = dt(2015, 8, 24)
    
    trains = get_trainId(start_date, end_date)

    pool = mp.Pool(4)

    pool.starmap(upload_ELsearch, [(i, start_date, end_date) for i in trains])

    pool.close()
 
