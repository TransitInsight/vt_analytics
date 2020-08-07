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
from dateutil.relativedelta import relativedelta, MO
import re
from plotly.subplots import make_subplots

import util as util

def get_fault_count_per_month():
    query = ("SELECT HISTOGRAM(loggedAt, INTERVAL 1 Month) as loggedMonth, count(*) as faultcount"
    "  FROM dlr_vobc_fault where faultCode > 0 group by loggedMonth")
    L = util.run_query(query)
    return L

def get_distance_per_month():
    query = ("SELECT HISTOGRAM(loggedAt, INTERVAL 1 Month) as loggedMonth, SUM(distance) as Distance "
    " FROM dlr_train_move group by loggedMonth")
    L = util.run_query(query)
    return L

def get_operating_hours_by_month():
    query = ("SELECT loggedMonth, sum(op_time) from op_hours group by loggedMonth")
    L = util.run_query(query)
    L = L.dropna()
    return L

def gen_faultcount_distance_ophour_list(start_date, end_date):
    df = get_fault_count_per_month()
    df2 = get_distance_per_month()
    df3 = get_operating_hours_by_month()
    df = df.set_index('loggedMonth').tz_localize(None)
    df2 = df2.set_index('loggedMonth').tz_localize(None)
    df3 = df3.set_index('loggedMonth').tz_localize(None)  
    df = df.join(df2)
    df = df.join(df3)
    df = df.reset_index()
    mask = (df['loggedMonth'] > start_date) & (df['loggedMonth'] <= end_date)
    df = df.loc[mask]
    data=df.to_dict('rows')
    return data 

def gen_faultcount_per_month(start_date, end_date):
    df = get_fault_count_per_month()
    mask = (df['loggedMonth'] > start_date) & (df['loggedMonth'] <= end_date)
    df = df.loc[mask]
    fig = go.Figure([go.Bar(x=df["loggedMonth"], y= df["faultcount"])])
    fig.update_layout(
    title="Fault Trending",
    yaxis_title="Fault Count",
    xaxis_title="Date",
    )
    return fig

def get_faults_by_type(start_date, end_date):
    start_date, end_date  = util.date2str2(start_date, end_date)
    query = ("SELECT faultCode, count(*) as faultcount  FROM dlr_vobc_fault "
    " where faultCode > 0 and loggedAt >= '{}' and loggedAt < '{}' group by faultCode").format(start_date, end_date)
    L = util.run_query(query)
    return L

def gen_past_months_fault_by_type(end_date, month):
    end_date = dt.strptime(end_date, "%Y-%m-%d")
    start_date = end_date + relativedelta(months=-month)
    df = get_faults_by_type(start_date, end_date)
    if df.empty == True:
        return {}
    fig = go.Figure([go.Bar(x=df["faultCode"], y= df["faultcount"])])
    fig.update_layout(
    title=("Past {} months fault").format(month),
    yaxis_title="Fault Count",
    xaxis_title="Fault Type",
    )
    return fig

# def gen_past_6_months_fault_by_type(end_date):
#     start_date = end_date + relativedelta(months=-6)
#     df = get_faults_by_type(start_date, end_date)
#     fig = go.Figure([go.Bar(x=df["faultCode"], y= df["faultcount"])])
#     return fig

def get_fault_per_vobc(start_date, end_date):
    start_date, end_date  = util.date2str2(start_date, end_date)
    query = ("SELECT vobcid, count(*) as faultcount  FROM dlr_vobc_fault "
    " where faultCode > 0 and loggedAt >= '{}' and loggedAt < '{}' group by vobcid order by faultcount desc").format(start_date, end_date)
    L = util.run_query(query)
    return L
def get_op_hour_per_vobc(start_date, end_date):
    start_date, end_date  = util.date2str2(start_date, end_date)
    query = ("SELECT vobcid, sum(op_time) as hour from op_hours"
    " where loggedMonth >= '{}' and loggedMonth < '{}' group by vobcid").format(start_date, end_date)
    L = util.run_query(query)
    return L
def gen_top_vobc_fault_past_months(end_date, months):
    end_date = dt.strptime(end_date, "%Y-%m-%d")
    start_date = end_date + relativedelta(months=-months)
    df = get_fault_per_vobc(start_date, end_date)
    df2 = get_op_hour_per_vobc(start_date, end_date)
    if df.empty == True or df2.empty == True:
        return {}
    df = df.head(n=20)
    df = df.set_index('vobcid')
    df2 = df2.set_index('vobcid') 
    df = df.join(df2, how='left')
    df = df.sort_values(by=['vobcid'])
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    fig.add_trace(
        go.Bar(x=df.index, y= df["faultcount"]),
        secondary_y=False
        )

    fig.add_trace(
        go.Scatter(x=df.index, y=df["hour"],
                    mode='lines+markers',
                    #line_shape='linear',
                    connectgaps=True
                    ),
                    secondary_y=True
    )

    fig.update_layout(
    title=("Top Vobc Fault past {} months").format(months),
    xaxis_title="VobcId",
    )
    fig.update_yaxes(title_text="fault count", secondary_y=False)
    fig.update_yaxes(title_text="operating hours", secondary_y=True)

    return fig



def get_fault_types_per_day(start_date, end_date):
    start_date, end_date  = util.date2str2(start_date, end_date)
    query = ("SELECT HISTOGRAM(loggedAt, INTERVAL 1 Day) as loggedDay, faultName, count(*) as faultcount FROM dlr_vobc_fault "
    " where faultCode > 0 and loggedAt >= '{}' and loggedAt < '{}' group by faultName, loggedDay").format(start_date, end_date)
    L = util.run_query(query)
    return L

def get_fault_names(start_date, end_date):
    start_date, end_date  = util.date2str2(start_date, end_date)
    query = ("SELECT faultName FROM dlr_vobc_fault "
    " where faultCode > 0 and loggedAt >= '{}' and loggedAt < '{}' group by faultName").format(start_date, end_date)
    L = util.run_query(query)
    if L.empty == False:
        return L["faultName"].tolist()
    return []
def get_fault_name(faultCode):
    query = ("SELECT faultName FROM dlr_vobc_fault "
    " where faultCode = {} group by faultName").format(faultCode)
    L = util.run_query(query)
    if L.empty == False:
        return L["faultName"].tolist()
    return []

def gen_fault_trend_bar(start_date,months,faultCode = None):
    start_date = dt.strptime(start_date, "%Y-%m-%d")
    end_date = start_date + relativedelta(months=months)
    df = get_fault_types_per_day(start_date, end_date)
    if faultCode == None:
        faults = get_fault_names(start_date, end_date)
    else:
        faults = get_fault_name(faultCode)
    
    fig = go.Figure()
    for faultName in faults:
        fig.add_trace(go.Bar(name=('Fault Name: {}').format(faultName), x=df["loggedDay"], y=df["faultcount"]),)
    
    fig.update_layout(barmode='stack')
    return fig

