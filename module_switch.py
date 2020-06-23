
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

def get_switch_count(start_date, end_date):
    start_date, end_date = util.date2str2(start_date,end_date)

    query = ("SELECT switchId, COUNT(*) as amt from dlr_switch_move" 
            " where interval >= 0 and intervalDesc in ('Moving Time to Left' , 'Moving Time to Right' )" 
            " and loggedAt >= '{}' and loggedAt < '{}'" 
            " group by switchId").format( start_date, end_date)
    
    L = util.run_query(query)

    return L

def get_switch_filter_val(start_date, end_date, switchId, Limit):
    start_date, end_date = util.date2str2(start_date,end_date)
    Limit = int(Limit)
    query = ("SELECT interval, switchId from dlr_switch_move"
            " where interval > 0 and intervalDesc in ('Moving Time to Left' , 'Moving Time to Right' )"
            " and switchId = '{}' and loggedAt >= '{}' and loggedAt < '{}'" 
            " order by interval desc LIMIT {}").format(switchId, start_date, end_date, Limit)
    
    L = util.run_query(query)
    if L is None or L.empty:
        return 0
    return L["interval"].min()

# start_date = dt(2012, 1, 1)
# end_date = dt(2020, 1, 1)
# start_date, end_date  = util.date2str2(start_date, end_date )

# def get_switch_filter_val( row, start_date = start_date, end_date = end_date):
#     switchId = row[1]
#     Limit = row[2]
#     start_date, end_date = util.date2str2(start_date,end_date)
#     Limit = int(Limit)
#     query = ("SELECT interval, switchId from dlr_switch_move"
#             " where interval > 0 and intervalDesc in ('Moving Time to Left' , 'Moving Time to Right' )"
#             " and switchId = '{}' and loggedAt >= '{}' and loggedAt < '{}'" 
#             " order by interval desc LIMIT {}").format(switchId, start_date, end_date, Limit)
    
#     L = util.run_query(query)
#     if L is None or L.empty:
#         return 0
#     return L["interval"].min()

def get_avg(start_date, end_date, switchId, interval_max):
    start_date, end_date = util.date2str2(start_date,end_date) 
    query = ("SELECT AVG(interval) as int_Avg from dlr_switch_move"
            " where interval > 0 and interval < {}  and intervalDesc in ('Moving Time to Left' , 'Moving Time to Right' )"
            " and switchId = '{}' and loggedAt >= '{}' and loggedAt < '{}'" 
            ).format(interval_max, switchId, start_date, end_date)
    
    L = util.run_query(query)
    if L is None or L.empty:
        return 0
    return L["int_Avg"].min()

def get_min(start_date, end_date, switchId, interval_max):
    start_date, end_date = util.date2str2(start_date,end_date)
    query = ("SELECT interval from dlr_switch_move"
            " where interval > 0 and interval < {}  and intervalDesc in ('Moving Time to Left' , 'Moving Time to Right' )"
            " and switchId = '{}' and loggedAt >= '{}' and loggedAt < '{}'" 
            " order by interval ASC LIMIT 5").format(interval_max, switchId, start_date, end_date)

    L = util.run_query(query)
    if L is None or L.empty:
        return 0
    return L["interval"].min()

def get_d0(start_date, end_date, switchId, avg):
    start_date, end_date = util.date2str2(start_date,end_date)

    query = ("SELECT AVG(interval) as int_Avg from dlr_switch_move"
            " where interval > 0 and interval <= {}  and intervalDesc in ('Moving Time to Left' , 'Moving Time to Right' )"
            " and switchId = '{}' and loggedAt >= '{}' and loggedAt < '{}'" 
            ).format(avg, switchId, start_date, end_date)

    L = util.run_query(query)
    if L is None or L.empty:
        return 0
    return L["int_Avg"].min()

def get_d1(start_date, end_date, switchId, avg, interval_max):
    start_date, end_date = util.date2str2(start_date,end_date)
    
    query = ("SELECT AVG(interval) as int_Avg from dlr_switch_move"
            " where interval > {} and interval < {}  and intervalDesc in ('Moving Time to Left' , 'Moving Time to Right')"
            " and switchId = '{}' and loggedAt >= '{}' and loggedAt < '{}'" 
            ).format(avg, interval_max, switchId, start_date, end_date)

    L = util.run_query(query)
    if L is None or L.empty:
        return 0
    return L["int_Avg"].max()

def get_df(start_date, end_date, filterout): 
    df = get_switch_count(start_date, end_date)
    df["amt"] = df["amt"]*filterout
    df['max'] = df.apply(lambda row: get_switch_filter_val(start_date, end_date, row["switchId"], row["amt"]), axis=1)
    return df

def get_df_2(pool, start_date, end_date,filterout): 
    df = get_switch_count(start_date, end_date)
    df["amt"] = df["amt"]*filterout
    df['max'] = pool.starmap(get_switch_filter_val, [(start_date, end_date, df["switchId"][ind], df["amt"][ind]) for ind in df.index])
    return df
 

def update_val(df,start_date, end_date):
    df["avg"] = df.apply(lambda row: get_avg(start_date, end_date, row["switchId"], row["max"]), axis=1)
    df["min"] = df.apply(lambda row: get_min(start_date, end_date, row["switchId"], row["max"]), axis=1)
    df["d0"] = df.apply(lambda row: get_d0(start_date,end_date, row["switchId"], row["avg"]), axis=1)
    df["d1"] = df.apply(lambda row: get_d1(start_date,end_date, row["switchId"], row["avg"], row["max"]), axis=1)
    
    return df


def update_val_s(df, ind, start_date, end_date):
    swid = df["switchId"][ind]
    mx = df["max"][ind]
    avg = get_avg(start_date, end_date, swid, mx) 
    L = get_min(start_date, end_date, swid, mx)  
    d0 = get_d0(start_date,end_date, swid, avg)  

    d1 = get_d1(start_date,end_date, swid, avg, mx)  
    return [avg, L, d0, d1]
  

def update_val_2(df, pool, start_date, end_date):

    data = pool.starmap(update_val_s, [(df, ind, start_date, end_date) for ind in df.index])
    df1 = pd.DataFrame(data, columns = ["avg", 'min', "d0", 'd1'])
    df["avg"] = df1["avg"] 
    df["min"] = df1["min"] 
    df["d0"] = df1["d0"] 
    df["d1"] = df1["d1"] 
    return df




def gen_graph(df):
    Lof = df['min'].tolist()
    d0 = df['d0'].tolist()
    avg = df['avg'].tolist()
    d1 = df['d1'].tolist()
    Uof = df['max'].tolist()

    fig = go.Figure()
    
    fig.add_trace(go.Box(
                q1=d0, 
                median=avg,
                q3=d1, 
                lowerfence=Lof,
                upperfence=Uof
                    ))
    return fig 

if __name__ == "__main__":
    start_date = dt(2014, 1, 1)
    end_date = dt(2020, 1, 1)
    start_date, end_date  = util.date2str2(start_date, end_date )
    
      
    #time.sleep(10)

    start = time.time()
    df = get_df(start_date, end_date, 0.01)
    df = update_val(df, start_date, end_date)
    print(df)
    end = time.time()
    print(end - start)

      
    

    start = time.time()
    pool = mp.Pool(4)
    df2 = get_df_2(pool, start_date, end_date, 0.01)
    df2 = update_val_2(df2, pool, start_date, end_date)
    print(df2)
    end = time.time()
    print(end - start)
    pool.close()
    #df = update_val(df,start_date, end_date)
    #fig = gen_graph(df)
    #fig.show()