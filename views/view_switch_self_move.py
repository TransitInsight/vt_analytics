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

from modules import module_switch_self_move as mss
from modules import module_switch as ms

import util as util

filter_start_date = dt(2014, 1, 1)
filter_end_date = dt(2016, 1, 1)
filter_start_date, filter_end_date  = util.date2str2(filter_start_date, filter_end_date )

layout = html.Div([
        
    html.Div([    
        
          
            dcc.Graph(id = '3d_ssw', 
                figure = mss.gen_graph_3d(),
                style={ 'float': 'Left', "display":"block",'width': "60vw","height" : "100vh"} 
            ),
            
            ]),
            
            dcc.Graph(id = 'line_ssw' ,
                 style={ 'float': 'right', "display":"block",'width': "38vw"} 
            ),
             dcc.Graph(id = 'boxplot_ssw' ,
                 style={ 'float': 'right', "display":"block",'width': "38vw"} 
            ),

    ])





@app.callback(Output('line_ssw', 'figure'),[
                Input('3d_ssw', 'clickData'),
                ])
def update_switchid_self_move_line_dates(clickData):
    return _switchid_self_move_line_dates(clickData)

def _switchid_self_move_line_dates(clickData):
    
    if clickData is None:
        return {}

    switchId= clickData['points'][0]['y']
    date = clickData['points'][0]['x']
    date = util.str2date1(date)
    start = date - timedelta(hours=12)
    end = start + timedelta(hours=23.5) 

    fig = ms.create_switchId_line_fig(switchId, start, end)
    fig.update_layout(
    #title="SwitchId: {} Switching data".format(switchId),
    xaxis_title="Time",
    yaxis_title = "SwitchId: {} Switching data".format(switchId),
    showlegend=False,
    #height= 300, 
    margin = dict(l = 20 , r = 20, t = 0)
    )

    return fig


@app.callback(Output('boxplot_ssw', 'figure'),[
                Input('3d_ssw', 'clickData'),
                ])
def update_switchid_self_move_bxplt(clickData):
    return _switchid_self_move_bxplt(clickData)

def _switchid_self_move_bxplt(clickData):
    if clickData is None:
        return {}
    
    switchId= clickData['points'][0]['y']
    date = clickData['points'][0]['x']
    date = util.str2date1(date)

    day  = 30
    start = date - timedelta(days=day)
    end = date + timedelta(days=day) 
    
    
    df = ms.gen_box_date_df(switchId, start, end)
    if df.empty:
        return {}
    data = ms.gen_box_graph(df, "100%")
    data.update_layout(
    #title="SwitchId: {} Switching time by date".format(switchId),
    xaxis_title="Dates",
    yaxis_title="SwitchId: {} Switching time by date".format(switchId),
    showlegend=False,
    xaxis = {
    #'tickformat' : '%d-%m-%y',
    'categoryorder' : 'category ascending'   
    },

    margin = dict(l = 20 , r = 20, t = 0)
    )
    

    return data