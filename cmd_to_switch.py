
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

from modules import module_switch as ms
import json
import requests
import util as util
from elasticsearch import Elasticsearch
from elasticsearch import helpers



start_date = dt(2014, 1, 1)
end_date = dt(2015, 12, 31)
start_date, end_date  = util.date2str2(start_date, end_date )

def get_switchId(start_date, end_date):
    start_date, end_date  = util.date2str2(start_date, end_date )
    query = ("SELECT switchId from dlr_switch_move where loggedAt >= '{}' and loggedAt < '{}' "
    " group by switchId").format(start_date, end_date)
    L = util.run_query(query)
    L = L["switchId"].tolist()
    return L


def getcmd_switch_times(df):
    val = 0
    loggedAt= []
    moved_t = []
    cont = True
    
    for ind in df.index:
        if df['switchCommand'][ind] != 0: 
            val = df['switchCommand'][ind]
            t1 = df['loggedAt'][ind]
            cont = True
        if val == df['positionDesc'][ind] and cont == True:
            loggedAt.append(t1.isoformat())
            t2 = df['loggedAt'][ind] - t1
            t2 = t2.total_seconds()
            moved_t.append(t2)
            cont = False

    data = pd.DataFrame(loggedAt,columns =['loggedAt'])
    data["moved_t"] = moved_t
    return data

def gen_cmd_to_switch_by_dates(switchId, startDate, endDate):
    mapping = {'Left': 1, 'Right': 2}
    data = pd.DataFrame()
    while startDate < endDate:
        end = startDate + timedelta(days=1)
        start_, end_  = util.date2str2(startDate, end)
        df = ms.get_switch_linechart_data(switchId, start_, end_)
        if df is not None:
            if df.empty == False:
                df = df.replace({'positionDesc': mapping})
                data = data.append(getcmd_switch_times(df))
        startDate = end
    data["switchId"] = switchId
    data = data.reset_index()
    data = data.drop(columns=["index"])
    return data



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




def upload_ELsearch(switchId, startDate, endDate):
    df = gen_cmd_to_switch_by_dates(switchId, startDate, endDate)
    df['loggedAt'] = df['loggedAt'].astype(str)
    insertDataframeIntoElastic(df, "cmd_to_switch")
    print("*")
    #return df
    


if __name__ == "__main__":
    start_date = dt(2014, 1, 1)
    end_date = dt(2015, 12, 31)
    switches = get_switchId(start_date, end_date)
    df = pd.DataFrame()
    pool = mp.Pool(5)
    
    df.append(pool.starmap(upload_ELsearch, [(i, start_date, end_date) for i in switches]))

    pool.close()
    #insertDataframeIntoElastic(df, "cmd_to_switch")
