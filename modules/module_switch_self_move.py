
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


def get_switch_amts(SwitchId):
    query = ("SELECT * from switch_self_move where switchId = {} and amt > 10 order by amt desc").format(SwitchId)
    L = util.run_query(query)
    return L

# def gen_graph(switchId):
#     df = get_switch_amts(switchId)
#     if df.empty:
#         return {}
#     x_data = df["Dates"].to_list()
#     y_data = df["amt"].to_list()
#     fig = go.Figure(data=go.Scatter(x=x_data, y=y_data, mode='markers'))
#     return fig

def get_switch_count():
    query = ("SELECT switchId, count(*) as count from dlr_switch_move where intervalDesc in ('Moving Time to Left' , 'Moving Time to Right' ) group by switchId order by count desc")
    L = util.run_query(query)
    return L

def gen_3d_df():
    switches = get_switch_count()
    switches = switches[switches["count"] > 76000]
    switches = switches["switchId"].to_list()
    df = pd.DataFrame()
    for i in switches:
        df = df.append(get_switch_amts(i))
    return df

def gen_graph_3d():
    df = gen_3d_df()
    if df.empty:
        return {}
    x_data = df["Dates"].to_list()
    z_data = df["amt"].to_list()
    y_data = df["switchId"].to_list()
    fig = go.Figure(data=[go.Scatter3d(
    x=x_data, 
    z=z_data,
    y=y_data,
    mode='markers',
    marker=dict(
        color= df["switchId"].to_list(),               
        #colorscale='Viridis',
        sizemode = 'area', 
        size = 3, 
        opacity=0.8
    )
    )])
    return fig







