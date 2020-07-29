
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
#import index 

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
#start_date, end_date  = util.date2str2(start_date, end_date )



def get_switchId():
    query = ("SELECT switchId from dlr_switch_move group by switchId")
    L = util.run_query(query)
    L = L["switchId"].tolist()
    return L


def gen_switching_counts(df):    
    prev = 0
    date = df["loggedAt"].min() 
    val = 0
    d_amt = []
    d_date = []
    for ind in df.index:
        if val == df['switchCommand'][ind]:
            pass
        else:
            d_date.append(date.isoformat())
            d_amt.append(ind - prev)
            val = df['switchCommand'][ind]
            prev = ind
            date = df['loggedAt'][ind]
    data = pd.DataFrame(d_date,columns =['Dates'])
    data["amt"] = d_amt
    indexNames = data[ data['amt'] <= 3 ].index
    data.drop(indexNames , inplace=True)
    return data


def gen_switching_counts_by_dates(switchId, startDate, endDate):
    data = pd.DataFrame()
    while startDate < endDate:
        end = startDate + timedelta(days=2)
        start_, end_  = util.date2str2(startDate, end)
        df = ms.get_switch_linechart_data(switchId, start_, end_)
        if df is not None:
            if df.empty == False:
                data = data.append(gen_switching_counts(df))
        startDate = end
    data["switchId"] = switchId
    data = data.reset_index()
    data = data.drop(columns=["index"])
    return data
    



def insertDataframeIntoElastic(dataFrame,index='index', typ = 'test', server = 'http://localhost:9200',
                           chunk_size = 2000):
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
        i = i+chunk_size



def upload_ELsearch(switchId, startDate, endDate):
    df = gen_switching_counts_by_dates(switchId, startDate, endDate)
    df['Dates'] = df['Dates'].astype(str)
    return df
    #insertDataframeIntoElastic(df, "switch_self_move")


if __name__ == "__main__":
    start_date = dt(2015, 12, 1)
    end_date = dt(2015, 12, 31)
    switches = get_switchId()
    df = pd.DataFrame()
    pool = mp.Pool(5)
    
    df = df.append(pool.starmap(upload_ELsearch, [(i, start_date, end_date) for i in switches]))

    pool.close()
    insertDataframeIntoElastic(df, "switch_self_move")



