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

import util as util

filter_start_date = dt(2015, 1, 1)
filter_end_date = dt(2016, 1, 1)
filter_start_date, filter_end_date  = util.date2str2(filter_start_date, filter_end_date )


def datecheck(start_date, end_date):
    if start_date is None:
        start_date = filter_start_date
    if end_date is None:
        end_date = filter_end_date 

    if start_date > end_date:
        t = end_date
        end_date = start_date
        start_date = t

    return start_date,end_date



date_sw = dcc.DatePickerRange(
            id='date-range_sw',
            min_date_allowed=filter_start_date,
            max_date_allowed=dt.today() + timedelta(days=1),
            start_date=filter_start_date,
            end_date=filter_end_date,
            style={ 'display':'inline-block', 'font_size': '100%', 'width':'300px','margin-top':'2px'}
        )


checkboxdict = [{'label':"All", "value": -1},
                {'label':"0.01%", "value":0.0001},
                {'label':"0.05%", "value":0.0005},
                {'label':"0.1%", "value":0.001},
                {'label':"0.5%", "value":.005},
                {'label':"1%", "value":0.01}]
filter_dropdown_sw = dcc.Dropdown(
                id = 'filter_out_dropdown',
                options= checkboxdict,
                value = 0.0001,
                style={ 'display':'inline-block', 'font-size':'100%', 'width': '200px', 'margin-top':'2px'},
            )

layout = html.Div([

    html.Div([
       
        dbc.Row(
                [
                    dbc.Col(html.Div("Date Range : ", style={'margin-top':'11px', 'font-size':'100%'}), width='auto'),
                    dbc.Col(date_sw, width='auto'),
                    dbc.Col(html.Div("filter amount : ", style={'margin-top':'11px', 'font-size':'100%'}), width='auto'),
                    dbc.Col(filter_dropdown_sw, width='auto')
                ]
                )
        ] ),
        
    html.Div([    
        
          
            dcc.Graph(id = 'BoxGraph_sw', 
                  
            ),
            
            ]),
        

    ])



@app.callback(Output('BoxGraph_sw', 'figure'),[
                Input('date-range_sw', 'start_date'),
                Input('date-range_sw', 'end_date'),
                Input('filter_out_dropdown', 'value'),
                ])
def update_switchid_boxplot(start_date,end_date, filter_out_dropdown):
    return _switchid_boxplot(start_date,end_date, filter_out_dropdown)

def _switchid_boxplot(start_date,end_date, filter_out_dropdown):
    start_date,end_date = datecheck(start_date, end_date)
    pool = None
    #pool = mp.Pool(4)
    df = ms.get_df(pool, start_date, end_date, filter_out_dropdown)
    df = ms.update_val(pool, df, start_date, end_date)
    #pool.close()
    
    if len(df.index) == 0 or df is None:
        data_1 = []
    else:
        data_1 = [ms.gen_graph(df)]          
   
    return{'data': data_1,                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 
            'layout' : go.Layout(title = "SwitchId_boxplot", 
                xaxis = {'title': 'SwitchId', 'categoryorder' : 'category ascending'},
                yaxis = {'title': 'Time to switch'},  
                hovermode="closest",
                clickmode =  'event+select')
            }

