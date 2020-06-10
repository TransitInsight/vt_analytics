#%%
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
import json
from datetime import datetime as dt
from datetime import timedelta
import re

from modules import module_vobcfault
from modules import module_commLoss
from views.ViewTrainmoveClass import ViewTrainmoveClass
from views.ViewFaultListClass import ViewFaultListClass

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


def gen_scatter_graph(df, datax, datay, text_field, bubble_size, size_scale):
    data = go.Scatter(x = datax, 
                    y = datay,
                    text = df[text_field],
                    mode = "markers", 
                    marker=dict(
                        size=bubble_size/max(bubble_size) *size_scale,
                        color=bubble_size, 
                        colorscale='Viridis',
                        sizemode = 'area', 
                        showscale=True)
                        )
    return data

def gen_scatter_graph_data(df, xfield, yfield, size_scale):
    datax = df[xfield].tolist()
    datay = df[yfield].tolist()
    comLoss = df["commLossCount"].tolist()
    comLoss = np.array(comLoss)
    data = gen_scatter_graph(df, datax, datay, "commLossCount", comLoss, size_scale)   
    return data

def gen_bar_data(df):
    datax = df['date'].tolist()
    datay = df['commLossCount'].tolist()
    fig = go.Bar(x=datax, y=datay)
    return fig

date = dcc.DatePickerRange(
            id='date-range_cL',
            min_date_allowed=filter_start_date,
            max_date_allowed=dt.today() + timedelta(days=1),
            start_date=filter_start_date,
            end_date=filter_end_date,
            style={ 'display':'inline-block', 'font_size': '100%', 'width':'300px','margin-top':'2px'}
        )

velocity_dropdown = dcc.Dropdown(
        id='velocity_dropdown_cL',
        options=[
            {'label': 'Zero_Velocity', 'value': 0},
            {'label': 'nonZero_Velocity', 'value': 1},
            {'label': 'Both', 'value': -1}
        ],
        value=-1,
        style={ 'display':'inline-block', 'font-size':'100%', 'width': '250px', 'margin-top':'2px'},
    )

apstatus_dropdown = dcc.Dropdown(
        id='apstatus_dropdown_cL',
        options=[
            {'label': 'Active', 'value': 1},
            {'label': 'Passive', 'value': 0},
            {'label': 'Both', 'value': -1}
        ],
        value=-1,
        style={ 'display':'inline-block', 'font-size':'100%', 'width': '250px', 'margin-top':'2px'},
    )


layout = html.Div([

    html.Div([
       
        dbc.Row(
                [
                    dbc.Col(html.Div("Date Range : ", style={'margin-top':'11px', 'font-size':'100%'}), width='auto'),
                    dbc.Col(date, width='auto'),
                    dbc.Col(html.Div("Velocity Choice : ", style={'margin-top':'11px', 'font-size':'100%'}), width='auto'),
                    dbc.Col(velocity_dropdown, width='auto'),
                    dbc.Col(html.Div("Active Passive State : ", style={'margin-top':'11px', 'font-size':'100%'}), width='auto'),
                    dbc.Col(apstatus_dropdown, width='auto'),
                ]
                )
        ] ),
        
    html.Div([    
        
            dcc.Graph(id = 'Scatterplot_cL',  
                style={ 'float': 'left', "display":"block", "height" : "63vh",'width': "63vw"},
                
            ),

            dcc.Graph(id = 'BarGraph_cL', 
                style={ 'float': 'right', "display":"block", "height" : "33vh",'width': "36vw"},  
            ),
            
            ]),
              
        

    ])


@app.callback(Output('Scatterplot_cL', 'figure'),[
                Input('date-range_cL', 'start_date'),
                Input('date-range_cL', 'end_date'),
                Input('velocity_dropdown_cL', 'value'),
                Input('apstatus_dropdown_cL', 'value')])
def update_Scatter(start_date,end_date, velocity_dropdown, apstatus):
    return _update_Scatter(start_date,end_date, velocity_dropdown,apstatus)

def _update_Scatter(start_date,end_date, velocity_dropdown, apstatus):
    start_date,end_date = datecheck(start_date, end_date)

    df = module_commLoss.get_commLoss_by_vobcid_loc(start_date, end_date, velocity_dropdown, apstatus)
    
    if len(df.index) == 0 or df is None:
        data_1 = []
    else:
        data_1 = [gen_scatter_graph_data(df,"locationName", "vobcid", 1000)]          
   
    return{'data': data_1,                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 
            'layout' : go.Layout(title = "CommLoss by VOBCID and LOCATION", 
                xaxis = {'title': 'Location', 'categoryorder' : 'category ascending'},
                yaxis = {'title': 'VOBCID'}, 
                #dragmode = False, 
                hovermode="closest",
                clickmode =  'event+select')
            }

@app.callback(
    Output('BarGraph_cL', 'figure'),[
    Input('Scatterplot_cL', 'clickData'),
    Input('date-range_cL', 'start_date'),
    Input('date-range_cL', 'end_date'),
    Input('velocity_dropdown_cL', 'value'),
    Input('apstatus_dropdown_cL', 'value')])
def display_click_data(clickData, start_date, end_date, velocity_dropdown, apstatus ):
    return _display_click_data(clickData, start_date, end_date, velocity_dropdown, apstatus  )

def _display_click_data(clickData, start_date, end_date, velocity_dropdown, apstatus):
    if clickData is None:
        data_1 = []
        vobcid_= "None"
        location = "None"
    else:
        vobcid_= clickData['points'][0]['y']
        location = clickData['points'][0]['x']

        start_date,end_date = datecheck(start_date, end_date)
      
        df = module_commLoss.get_commLoss_by_vobcid_loc_date(start_date, end_date, vobcid_, location, velocity_dropdown, apstatus)

        if len(df.index) == 0 or df is None:
            data_1 = []
        else:
            data_1 = [gen_bar_data(df)]

    return{'data': data_1,                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 
            'layout' : go.Layout(title = "CommLoss by Date VOBCID: {} Location: {}".format(vobcid_, location), 
                xaxis = {'title': 'Date' },
                #dragmode = False,
                yaxis = {'title': 'CommLoss Count'}, 
                hovermode="closest")
            }