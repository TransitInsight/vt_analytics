
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
    if L is None or L.empty:
        return 0
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


def query_interval_by_date(switch_id, start_date, end_date):

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
                            "value" : switch_id,
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

def gen_df(start_date, end_date):

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
    # Lof = df['min'].tolist()
    # d0 = df['d0'].tolist()
    # avg = df['avg'].tolist()
    # d1 = df['d1'].tolist()
    # Uof = df['max'].tolist()

    fig = go.Figure()
    
    # fig.add_trace(go.Box(
    #             q1=d0, 
    #             median=avg,
    #             q3=d1, 
    #             lowerfence=Lof,
    #             upperfence=Uof,
    #             marker_color= "#FFA07A",
                
    #                 ))
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

def gen_graph(pool, start_date, end_date, filter_Val):
    # start_date, end_date = util.date2str2(start_date,end_date)
    # pool = mp.Pool(4)
    # df = get_df(pool, start_date, end_date, filterout)
    # df = update_val(pool, df,start_date, end_date)
    df = gen_df(start_date,end_date)
    df2 = get_unlock_count( start_date, end_date)
    df = df.set_index('switchId').join(df2.set_index('switchId'))
    df = df.fillna(value = 0)
    
    if len(df.index) == 0 or df is None:
        data_1 = []
    else:
        data_1 = gen_graph_(df, filter_Val)

    #pool.close()
    return data_1 

#def get_df(start_date, end_date, filterout): 
#     df = get_switch_count(start_date, end_date)
#     df["amt"] = df["amt"]*filterout
#     df['max'] = df.apply(lambda row: get_switch_filter_val(start_date, end_date, row["switchId"], row["amt"]), axis=1)
#     return df

# def update_val(df,start_date, end_date):
#     df["avg"] = df.apply(lambda row: get_avg(start_date, end_date, row["switchId"], row["max"]), axis=1)
#     df["min"] = df.apply(lambda row: get_min(start_date, end_date, row["switchId"], row["max"]), axis=1)
#     df["d0"] = df.apply(lambda row: get_d0(start_date,end_date, row["switchId"], row["avg"]), axis=1)
#     df["d1"] = df.apply(lambda row: get_d1(start_date,end_date, row["switchId"], row["avg"], row["max"]), axis=1)
    
#     return df

# def get_switch_count(start_date, end_date):

#     query = ("SELECT switchId, COUNT(*) as amt from dlr_switch_move" 
#             " where interval >= 0 and intervalDesc in ('Moving Time to Left' , 'Moving Time to Right' )" 
#             " and loggedAt >= '{}' and loggedAt < '{}'" 
#             " group by switchId").format( start_date, end_date)
    
#     L = util.run_query(query)

#     return L

# def get_switch_filter_val(start_date, end_date, switchId, Limit):
#     if Limit != -1 and Limit != 0 and Limit > 1:
#         Limit = int(Limit)
#         Limit = 'LIMIT {}'.format(Limit)
#     else:
#         Limit = 'LIMIT 1'
#     query = ("SELECT interval, switchId from dlr_switch_move"
#             " where interval > 0 and intervalDesc in ('Moving Time to Left' , 'Moving Time to Right' )"
#             " and switchId = '{}' and loggedAt >= '{}' and loggedAt < '{}'" 
#             " order by interval desc {}").format(switchId, start_date, end_date, Limit)
    
#     L = util.run_query(query)
#     if L is None or L.empty:
#         return 0
#     return L["interval"].min()


# def get_avg(start_date, end_date, switchId, interval_max):
#     query = ("SELECT AVG(interval) as int_Avg from dlr_switch_move"
#             " where interval > 0 and interval <= {}  and intervalDesc in ('Moving Time to Left' , 'Moving Time to Right' )"
#             " and switchId = '{}' and loggedAt >= '{}' and loggedAt < '{}'" 
#             ).format(interval_max, switchId, start_date, end_date)
    
#     L = util.run_query(query)
#     if L is None or L.empty:
#         return 0
#     return L["int_Avg"].min()

# def get_min(start_date, end_date, switchId, interval_max):
#     query = ("SELECT interval from dlr_switch_move"
#             " where interval > 0 and interval <= {}  and intervalDesc in ('Moving Time to Left' , 'Moving Time to Right' )"
#             " and switchId = '{}' and loggedAt >= '{}' and loggedAt < '{}'" 
#             " order by interval ASC LIMIT 5").format(interval_max, switchId, start_date, end_date)

#     L = util.run_query(query)
#     if L is None or L.empty:
#         return 0
#     return L["interval"].min()

# def get_d0(start_date, end_date, switchId, avg):

#     query = ("SELECT AVG(interval) as int_Avg from dlr_switch_move"
#             " where interval > 0 and interval <= {}  and intervalDesc in ('Moving Time to Left' , 'Moving Time to Right' )"
#             " and switchId = '{}' and loggedAt >= '{}' and loggedAt < '{}'" 
#             ).format(avg, switchId, start_date, end_date)

#     L = util.run_query(query)
#     if L is None or L.empty:
#         return 0
#     return L["int_Avg"].min()

# def get_d1(start_date, end_date, switchId, avg, interval_max):
#     query = ("SELECT AVG(interval) as int_Avg from dlr_switch_move"
#             " where interval > {} and interval <= {}  and intervalDesc in ('Moving Time to Left' , 'Moving Time to Right')"
#             " and switchId = '{}' and loggedAt >= '{}' and loggedAt < '{}'" 
#             ).format(avg, interval_max, switchId, start_date, end_date)

#     L = util.run_query(query)
#     if L is None or L.empty:
#         return 0
#     return L["int_Avg"].max()

# # def get_max(start_date, end_date, switchId, interval_max):
    
# #     query = ("SELECT interval from dlr_switch_move"
# #             " where interval < {}  and intervalDesc in ('Moving Time to Left' , 'Moving Time to Right')"
# #             " and switchId = '{}' and loggedAt >= '{}' and loggedAt < '{}'" 
# #             " order by interval DESC LIMIT 5").format( interval_max, switchId, start_date, end_date)

# #     L = util.run_query(query)
# #     if L is None or L.empty:
# #         return 0
# #     return L["interval"].max()


# def get_df(pool, start_date, end_date,filterout): 
#     df = get_switch_count(start_date, end_date)
#     df["amt"] = df["amt"]*filterout
#     df['max'] = pool.starmap(get_switch_filter_val, [(start_date, end_date, df["switchId"][ind], df["amt"][ind]) for ind in df.index])
#     return df



# def update_val_s(df, ind, start_date, end_date):
#     swid = df["switchId"][ind]
#     mx = df["max"][ind]
#     avg = get_avg(start_date, end_date, swid, mx) 
#     L = get_min(start_date, end_date, swid, mx)  
#     d0 = get_d0(start_date,end_date, swid, avg)  
#     #max_ = get_max(start_date, end_date, swid, mx)

#     d1 = get_d1(start_date,end_date, swid, avg, mx)  
#     return [avg, L, d0, d1]
  

# def update_val(pool, df, start_date, end_date):

#     data = pool.starmap(update_val_s, [(df, ind, start_date, end_date) for ind in df.index])
#     df1 = pd.DataFrame(data, columns = ["avg", 'min', "d0", 'd1'])
#     df["avg"] = df1["avg"] 
#     df["min"] = df1["min"] 
#     df["d0"] = df1["d0"] 
#     df["d1"] = df1["d1"] 
#     #df["max_"] = df1["max_"] 
#     return df

# def get_df(p, start_date, end_date, filterout): 
#     df = get_switch_count(start_date, end_date)
#     df["amt"] = df["amt"]*filterout
#     df['max'] = df.apply(lambda row: get_switch_filter_val(start_date, end_date, row["switchId"], row["amt"]), axis=1)
#     return df

# def update_val(p, df,start_date, end_date):
#     df["avg"] = df.apply(lambda row: get_avg(start_date, end_date, row["switchId"], row["max"]), axis=1)
#     df["min"] = df.apply(lambda row: get_min(start_date, end_date, row["switchId"], row["max"]), axis=1)
#     df["d0"] = df.apply(lambda row: get_d0(start_date,end_date, row["switchId"], row["avg"]), axis=1)
#     df["d1"] = df.apply(lambda row: get_d1(start_date,end_date, row["switchId"], row["avg"], row["max"]), axis=1)
    
#     return df