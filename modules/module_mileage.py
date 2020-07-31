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
import dash_table

#import index 

from datetime import datetime as dt
from datetime import timedelta
import re

import util as util

def get_fleet_daily_mileage(start_date, end_date):
    start_date, end_date  = util.date2str2(start_date, end_date)
    query = ("SELECT loggedDate, SUM(distance)/1000 as daily_distance FROM dlr_train_move "
    " where loggedAt >= '{}' and loggedAt < '{}' group by loggedDate").format(start_date, end_date)
    L = util.run_query(query)
    return L
def gen_fleet_daily_mileage_graph(start_date, end_date):
    df = get_fleet_daily_mileage(start_date, end_date)
    if df.empty:
        return {}
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df["loggedDate"], y=df['daily_distance'],
                name = "fleet_daily_mileage_graph",
                line_color='blue', 
                mode='lines+markers',
                marker=dict(size=6, 
                            symbol='square',
                            color= 'blue'
                            ), 
                line_width=2,
                connectgaps=True,
                ) )
    return fig




def get_mileage_by_train(start_date, end_date):
    start_date, end_date  = util.date2str2(start_date, end_date)
    query = ("SELECT vobcid, SUM(distance)/1000 as Distance FROM dlr_train_move "
    " where loggedAt >= '{}' and loggedAt < '{}' group by vobcid").format(start_date, end_date)
    L = util.run_query(query)
    return L

def gen_mileage_by_train_table(start_date):
    start_date = util.str2date1(start_date)
    end_date = start_date + timedelta(hours=24)
    df = get_mileage_by_train(start_date, end_date)
    df = df.dropna()
    if df.empty:
        return {}
    df["loggedDate"] = start_date    
    data=df.to_dict('rows')
    return data 
            


# def get_train_total_mileage(vobcid):
#     query = ("SELECT vobcid, SUM(distance)/1000 as Distance FROM dlr_train_move "
#     " where vobcid = {} group by vobcid").format(vobcid)
#     L = util.run_query(query)
#     if L.empty == False:
#         return L['Distance'].max()
#     return 0

def get_train_mileage_by_30min(vobcid, start_date, end_date):
    query = ("SELECT HISTOGRAM(loggedAt, INTERVAL 30 MINUTES) as time, SUM(distance) as Distance FROM dlr_train_move "
    " where vobcid = {} and loggedAt >= '{}' and loggedAt < '{}' group by time").format(vobcid, start_date, end_date)
    L = util.run_query(query)
    return L

def get_train_mileage_by_loop(vobcid, start_date, end_date):
    query = ("SELECT loopName, SUM(distance) as Distance FROM dlr_train_move "
    " where vobcid = {} and loggedAt >= '{}' and loggedAt < '{}' group by loopName").format(vobcid, start_date, end_date)
    L = util.run_query(query)
    return L

def gen_train_mileage_table(vobcid, start_date):
    start_date = util.str2date1(start_date)
    end_date = start_date + timedelta(hours=24)
    start_date, end_date  = util.date2str2(start_date, end_date)
    df = get_train_mileage_by_30min(vobcid, start_date, end_date)
    df = df.dropna()
    df2 = get_train_mileage_by_loop(vobcid, start_date, end_date)
    df2 = df2.dropna()
    df = df.append(df2, ignore_index=True, sort=False)
    if df.empty:
        return {}
    df["vobcid"] = vobcid   
    data=df.to_dict('rows')
    return data 

def get_train_total_mileage():
    query = ("SELECT vobcid, SUM(distance)/1000 as Distance FROM dlr_train_move "
    " group by vobcid").format()
    L = util.run_query(query)
    return L

def gen_train_total_mileage():
    df = get_train_total_mileage()
    df = df.dropna()
    fig = go.Figure([go.Bar(x=df["vobcid"], y=df['Distance'])])
    return fig