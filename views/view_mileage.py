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

from modules import module_mileage as mm

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

date_vm = dcc.DatePickerRange(
            id='date-range_vm',
            min_date_allowed=dt(2000, 1, 1),
            max_date_allowed=dt.today() + timedelta(days=1),
            start_date=filter_start_date,
            end_date=filter_end_date,
            style={ 'display':'inline-block', 'font_size': '100%', 'width':'300px','margin-top':'2px'}
        )


layout = html.Div([

    html.Div([
       
        dbc.Row(
                [
                    dbc.Col(html.Div("Date Range : ", style={'margin-top':'11px', 'font-size':'100%'}), width='auto'),
                    dbc.Col(date_vm, width='auto'),
                ]
                )
        ] ),
        
          
            dcc.Graph(id = 'fleet_daily_mileage_graph', 
                 style={ 'float': 'right', "display":"block",'width': "98vw","height" : "33vh"} 
            ),
            
            html.Div([
            dash_table.DataTable(
                id='mileage_by_train',
                page_size=15,
                editable=False,
                columns=(
                    [
                        {'id': 'vobcid', 'name': 'VOBCID'},
                        {'id': 'Distance', 'name': 'Distance(KM)'},
                        {'id': 'loggedDate', 'name': 'Date'},
                    ] 
                ),
            )],style={ 'float': 'Left', "display":"block",'width': "25vw", 'margin-left':'50px'} ),

            html.Div([
            dash_table.DataTable(
                id= 'train_mileage',
                page_size=15,
                editable=False,
                columns=(
                    [
                        {'id': 'time', 'name': 'Time'},
                        {'id': 'loopName', 'name': 'loopName'},
                        {'id': 'Distance', 'name': 'Distance(M)'},
                        {'id': 'vobcid', 'name': 'VOBCID'},
                    ] 
                ),
            )],style={ 'float': 'Left', "display":"block",'width': "25vw", 'margin-left':'50px'} ),
             
            dcc.Graph(id = 'totals',
                figure = mm.gen_train_total_mileage(), 
                style={ 'float': 'Right', "display":"block",'width': "40vw","height" : "33vh"} 
            ),

    ])



@app.callback(Output('fleet_daily_mileage_graph', 'figure'),[
                Input('date-range_vm', 'start_date'),
                Input('date-range_vm', 'end_date'),
                ])
def update_fleet_mileage(start_date,end_date):
    return _fleet_mileage(start_date,end_date)

def _fleet_mileage(start_date,end_date):
    start_date,end_date = datecheck(start_date, end_date)
    data =  mm.gen_fleet_daily_mileage_graph(start_date, end_date)
    data.update_layout(
    title="fleet_movement",
    yaxis_title="Distance(KM)",
    xaxis_title="Date",
    showlegend=False,
    height= 300, 
    margin = dict(l = 20 , r = 20, t = 0)
    )

    return data

@app.callback(Output('mileage_by_train', 'data'),[
                Input('fleet_daily_mileage_graph', 'clickData')
                ])
def update_mileage_by_train(clickData):
    return _mileage_by_train(clickData)

def _mileage_by_train(clickData):
    if clickData is None:
        return []
    start_date = clickData['points'][0]['x']
    data = mm.gen_mileage_by_train_table(start_date)

    return data

@app.callback(Output('train_mileage', 'data'),[
                Input('mileage_by_train', 'active_cell'),
                Input('mileage_by_train', 'derived_viewport_data'),
                #Input('fleet_daily_mileage_graph', 'clickData')
                ])
def update_train_mileage(table_active_cell, table_data):
    return _train_mileage(table_active_cell, table_data)

def _train_mileage(table_active_cell, table_data):
    # if clickData is None:
    #     return []
    if table_data is None or len(table_data) == 0:
        return[]
    if table_active_cell is None or len(table_data) < table_active_cell['row']:
        return[]
    
    #start_date = clickData['points'][0]['x']

    vobcid = table_data[table_active_cell['row']]['vobcid']
    start_date = table_data[table_active_cell['row']]['loggedDate'] 
    data = mm.gen_train_mileage_table(vobcid, start_date)

    return data

