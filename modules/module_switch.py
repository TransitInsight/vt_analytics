
import math
import numpy as np
import pandas as pd

import json
from datetime import datetime as dt
from datetime import timedelta
import re
import plotly.graph_objs as go
import multiprocessing as mp
import time 
import sys
import util as util

import config as cfg




def get_unlock_count( start_date, end_date): 
    query = ("SELECT switchId, COUNT(*) as count from dlr_switch_move"
    " where interval > 0 and loggedAt >= '{}' and loggedAt < '{}'" 
    " and intervalDesc in ('Moving Time to Left' , 'Moving Time to Right' ) "
    " and duration >= 10  group by switchId").format(start_date, end_date)

    L = util.run_query(query)
    return L
    
def get_unlock_count_by_date( switchId, start_date, end_date): 
    query = ("SELECT loggedDate, COUNT(*) as count from dlr_switch_move"
    " where interval > 0 and loggedAt >= '{}' and loggedAt < '{}' and switchId = {}" 
    " and intervalDesc in ('Moving Time to Left' , 'Moving Time to Right' ) "
    " and duration >= 10  group by loggedDate").format(start_date, end_date, switchId)

    L = util.run_query(query)
    return L



def query_interval_by_switch(start_date, end_date):

    start_date,end_date = util.date2str2(start_date,end_date)

    query_body = {
        "size": 0,
        "query" :  {
            "bool" : {
            "must" : [
                {
                "bool" : {
                    "must" : [
                    {
                        "terms" : {
                        "intervalDesc.keyword" : [
                            "Moving Time to Right",
                            "Moving Time to Left"
                        ],
                        "boost" : 1.0
                        }
                    },
                    {
                        "range" : {
                        "interval" : {
                            "from" : 0,
                            "to" : 2000,
                            "include_lower" : True,
                            "include_upper" : False,
                            "boost" : 1.0
                        }
                        }
                    }
                    ],
                    "adjust_pure_negative" : True,
                    "boost" : 1.0
                }
                },
                {
                "range" : {
                    "loggedAt" : {
                    "from" : start_date,
                    "to" : end_date,
                    "include_lower" : False,
                    "include_upper" : False,
                    "boost" : 1.0
                    }
                }
                }
            ],
            "adjust_pure_negative" : True,
            "boost" : 1.0
            }
        },

        "aggs": {
            "switchId": {
            "terms": {
                "field": "switchId",
                "size": 1000
            },

            "aggs": {
                "box_interval":{ 
                "percentiles": {
                    "field":"interval",
                    "percents": [
                    1,
                    25,
                    50,
                    75,
                    98,
                    98.5,
                    99,
                    99.5,
                    99.9,
                    100
                    ]
                } 
                }
            }
            }
        }
    }    

    result = util.run_query_es_native('dlr_switch_move',  query_body)
    return result


def query_interval_by_date(switchId, start_date, end_date):

    start_date,end_date = util.date2str2(start_date,end_date)

    query_body = {
        "size": 0,
        "query" :  {
            "bool" : {
            "must" : [
                {
                "bool" : {
                    "must" : [
                    {
                        "terms" : {
                        "intervalDesc.keyword" : [
                            "Moving Time to Right",
                            "Moving Time to Left"
                        ],
                        "boost" : 1.0
                        }
                    },
                    {
                        "term" : {
                        "switchId" : {
                            "value" : switchId,
                            "boost" : 1.0
                        }
                        }
                    }
                    ],
                    "adjust_pure_negative" : True,
                    "boost" : 1.0
                }
                },
                {
                "bool" : {
                    "must" : [
                    {
                        "range" : {
                        "interval" : {
                            "from" : 0,
                            "to" : None,
                            "include_lower" : True,
                            "include_upper" : False,
                            "boost" : 1.0
                        }
                        }
                    },
                    {
                        "range" : {
                        "loggedAt" : {
                            "from" : start_date,
                            "to" : end_date,
                            "include_lower" : False,
                            "include_upper" : False,
                            "boost" : 1.0
                        }
                        }
                    }
                    ],
                    "adjust_pure_negative" : True,
                    "boost" : 1.0
                }
                }
            ],
            "adjust_pure_negative" : True,
            "boost" : 1.0
            }
        },

        "aggs": {
            "opDate": {
            "terms": {
                "field": "loggedDate",
                "size": 1000
            },

            "aggs": {
                "box_interval":{ 
                "percentiles": {
                    "field":"interval",
                    "percents": [
                    1,
                    25,
                    50,
                    75,
                    98,
                    98.5,
                    99,
                    99.5,
                    99.9,
                    100
                    ]
                } 
                }
            }
            }
        }
    }


    result = util.run_query_es_native('dlr_switch_move',  query_body)
    return result

def gen_bx_df_(start_date, end_date):
    start_date, end_date = util.date2str2(start_date,end_date)
    result = query_interval_by_switch(start_date,end_date)
    Swid = []
    L = []
    d0 = []
    mean = []
    d1 = [] 
    U98 = []
    U985 = []
    U99 = []
    U995 = []
    U999 = []
    U = []
    for i in range(len(result['aggregations']['switchId']['buckets'])):
        Swid.append(result['aggregations']['switchId']['buckets'][i]['key'])
        L.append(result['aggregations']['switchId']['buckets'][i]['box_interval']['values']['1.0'])
        d0.append(result['aggregations']['switchId']['buckets'][i]['box_interval']['values']['25.0'])
        mean.append(result['aggregations']['switchId']['buckets'][i]['box_interval']['values']['50.0'])
        d1.append(result['aggregations']['switchId']['buckets'][i]['box_interval']['values']['75.0'])
        U98.append(result['aggregations']['switchId']['buckets'][i]['box_interval']['values']['98.0'])
        U985.append(result['aggregations']['switchId']['buckets'][i]['box_interval']['values']['98.5'])
        U99.append(result['aggregations']['switchId']['buckets'][i]['box_interval']['values']['99.0'])
        U995.append(result['aggregations']['switchId']['buckets'][i]['box_interval']['values']['99.5'])
        U999.append(result['aggregations']['switchId']['buckets'][i]['box_interval']['values']['99.9'])
        U.append(result['aggregations']['switchId']['buckets'][i]['box_interval']['values']['100.0'])

    df = pd.DataFrame( list(zip(Swid, L, d0, mean, d1, U98, U985, U99, U995, U999, U)), columns =['switchId', "min", "d0", "mean","d1","98%","98.5%","99%","99.5%", "99.9%", "100%"])
    return df


def gen_bx_date_df_(switchId, start_date, end_date):
    start_date, end_date = util.date2str2(start_date,end_date)
    result = query_interval_by_date(switchId, start_date, end_date)
    Ldate = []
    L = []
    d0 = []
    mean = []
    d1 = [] 
    D98 = []
    D985 = []
    D99 = []
    D995 = []
    D999 = []
    D = []
    for i in range(len(result['aggregations']['opDate']['buckets'])):
        Ldate.append(result['aggregations']['opDate']['buckets'][i]["key_as_string"]) 
        L.append(result['aggregations']['opDate']['buckets'][i]['box_interval']['values']['1.0'])
        d0.append(result['aggregations']['opDate']['buckets'][i]['box_interval']['values']['25.0'])
        mean.append(result['aggregations']['opDate']['buckets'][i]['box_interval']['values']['50.0'])
        d1.append(result['aggregations']['opDate']['buckets'][i]['box_interval']['values']['75.0'])
        D98.append(result['aggregations']['opDate']['buckets'][i]['box_interval']['values']['98.0'])
        D985.append(result['aggregations']['opDate']['buckets'][i]['box_interval']['values']['98.5'])
        D99.append(result['aggregations']['opDate']['buckets'][i]['box_interval']['values']['99.0'])
        D995.append(result['aggregations']['opDate']['buckets'][i]['box_interval']['values']['99.5'])
        D999.append(result['aggregations']['opDate']['buckets'][i]['box_interval']['values']['99.9'])
        D.append(result['aggregations']['opDate']['buckets'][i]['box_interval']['values']['100.0'])

    df = pd.DataFrame( list(zip( Ldate, L, d0, mean, d1, D98, D985, D99, D995, D999, D)), columns =["loggedDate", "min", "d0", "mean","d1","98%","98.5%","99%","99.5%", "99.9%", "100%"])
    return df

color_dict = {
    0: "#00BFFF", 
    1: "#FFA07A",
    2: "#FA8072", 
    3: "#CD5C5C", 
    4: "#DC143C",
    5: "#B22222", 
    6: "#FF0000",  
    }

def get_color(cnt):
    if cnt < 7:
        return color_dict[cnt]
    return '#8B0000'
def gen_graph_(df, filter_Val):

    fig = go.Figure()
    
    
    for ind in df.index:
        fig.add_trace(go.Box(
                x = [ind],
                q1=[df['d0'][ind]], 
                median=[df['mean'][ind]],
                q3=[df['d1'][ind]], 
                lowerfence=[df['min'][ind]],
                upperfence=[df[filter_Val][ind]],
                marker_color= get_color(df["count"][ind]),

        ))

    fig.update_xaxes(type="category")
    return fig 

def gen_box_df(start_date, end_date):
    start_date, end_date  = util.date2str2(start_date, end_date )
    df = gen_bx_df_(start_date,end_date)
    df2 = get_unlock_count( start_date, end_date)
    if df2 is not None:
        df = df.set_index('switchId').join(df2.set_index('switchId'))
        df = df.fillna(value = 0)
    else:
        df["count"] = 0 
    return df 

def gen_box_date_df(switchId, start_date, end_date):
    start_date, end_date  = util.date2str2(start_date, end_date )
    df = gen_bx_date_df_(switchId, start_date,end_date)
    df2 = get_unlock_count_by_date(switchId, start_date, end_date)
    df["loggedDate"] = pd.to_datetime(df["loggedDate"])
    # df["loggedDate"] = df["loggedDate"].tz_localize(None)
    df = df.set_index('loggedDate').tz_localize(None)
    if df2 is not None and not df2.empty:
        df2 = df2.set_index('loggedDate').tz_localize(None) 
        df = df.join(df2)
        df = df.fillna(value = 0)
    else:
        df["count"] = 0 
    return df 
    
def gen_box_graph(df, filter_Val):
    
    if len(df.index) == 0 or df is None:
        data_1 = []
    else:
        data_1 = gen_graph_(df, filter_Val)

    return data_1 



