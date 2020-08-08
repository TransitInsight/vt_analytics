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

from modules import module_fault_trend as mft

import util as util

filter_start_date = '2015-01-01'
filter_end_date = '2015-06-06'
#filter_start_date, filter_end_date  = util.date2str2(filter_start_date, filter_end_date )
end_date = dt(2015, 6, 1)
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

date_ft = dcc.DatePickerRange(
            id='date-range_ft',
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
                    dbc.Col(date_ft, width='auto'),
                ]
                )
        ] ),

        html.Div([
            html.Div([
            dash_table.DataTable(
                id='FaultList',
                page_size=10,
                editable=False,
                #data = mft.gen_faultcount_distance_ophour_list(),
                columns=(
                    [
                        {'id': 'loggedMonth', 'name': 'Date'},
                        {'id': 'Distance', 'name': 'Distance(KM)'},
                        {'id': 'faultcount', 'name': 'FaultCount'},
                        
                    ] 
                ),
            )],style={ 'float': 'Left', "display":"block",'width': "20vw", 'margin-left':'25px'} ),

          
            dcc.Graph(id = 'FaultTrending', 
                style={ 'float': 'Left', "display":"block",'width': "30vw","height" : "33vh", 'margin-left':'25px'} 
            ),
            dcc.Graph(id = 'Last_month_fault',               
                style={ 'float': 'Left', "display":"block",'width': "30vw","height" : "33vh", 'margin-left':'25px'} 
            ),
            dcc.Graph(id = 'Last_6_months_fault',               
                style={ 'float': 'Left', "display":"block",'width': "30vw","height" : "33vh"} 
            ),
             dcc.Graph(id = 'Last_month_fault_by_vobc',             
                style={ 'float': 'Left', "display":"block",'width': "30vw","height" : "33vh"} 
            ),
            dcc.Graph(id = 'Last_6_months_fault_by_vobc',           
                style={ 'float': 'Left', "display":"block",'width': "30vw","height" : "33vh"} 
            ),

            ],style={ 'float': 'Left', "display":"block",'width': "100vw"}),

            dcc.Graph(id = 'fault_type_bar',           
                style={ 'float': 'Left', "display":"block",'width': "100vw","height" : "33vh"} 
            ),
            html.Div([
            dash_table.DataTable(
                id='vobc_fault_list',
                page_size=30,
                editable=False,
                #data = mft.gen_faultcount_distance_ophour_list(),
                columns=(
                    [
                          
                        {'id': 'loggedAt', 'name': 'Date'},
                        {'id': 'faultCodeSet', 'name': 'FaultCodeSet'},
                        {'id': 'faultCode', 'name': 'FaultCode'},
                        {'id': 'parentTrainId', 'name': 'TrainID'},
                        {'id': 'vehicleName', 'name': 'VehicleName'},
                        {'id': 'vobcid', 'name': 'Vobcid'},
                        {'id': 'VobcStatus', 'name': 'VobcStatus'},
                        {'id': 'locationName', 'name': 'locationName'},
                        {'id': 'loopName', 'name': 'loopName'},
                        {'id': 'velocity', 'name': 'velocity'},
                        #{'id': 'duration', 'name': 'duration'},
                        {'id': 'faultDescription', 'name': 'faultDescription'},


                    ] 
                ),
            )],style={ 'float': 'left', "display":"block",'width': "90vw", 'margin-left':'50px'} ),
             
    ])


@app.callback(Output('FaultList', 'data'),[
                Input('date-range_ft', 'start_date'),
                Input('date-range_ft', 'end_date'),
                ])
def update_fc_list(start_date,end_date):
    return _fc_list(start_date,end_date)

def _fc_list(start_date,end_date):
    start_date,end_date = datecheck(start_date, end_date)
    data = mft.gen_faultcount_distance_ophour_list(start_date,end_date)
    return data

@app.callback(Output('FaultTrending', 'figure'),[
                Input('date-range_ft', 'start_date'),
                Input('date-range_ft', 'end_date'),
                ])
def update_fault_trend(start_date,end_date):
    return _fault_trend(start_date,end_date)

def _fault_trend(start_date,end_date):
    start_date,end_date = datecheck(start_date, end_date)
    data = mft.gen_faultcount_per_month(start_date,end_date)
    return data

@app.callback(Output('Last_month_fault', 'figure'),[
                Input('date-range_ft', 'end_date'),
                ])
def update_past_month_fault(end_date):
    data = mft.gen_past_months_fault_by_type(end_date, 1)
    return data

@app.callback(Output('Last_6_months_fault', 'figure'),[
                Input('date-range_ft', 'end_date'),
                ])
def update_past_6_month_fault(end_date):
    data = mft.gen_past_months_fault_by_type(end_date, 6)
    return data

@app.callback(Output('Last_month_fault_by_vobc', 'figure'),[
                Input('date-range_ft', 'end_date'),
                ])
def update_top_vobc_fault_1_month(end_date):
    data = mft.gen_top_vobc_fault_past_months(end_date, 1)
    return data

@app.callback(Output('Last_6_months_fault_by_vobc', 'figure'),[
                Input('date-range_ft', 'end_date'),
                ])
def update_top_vobc_fault_6_month(end_date):
    data = mft.gen_top_vobc_fault_past_months(end_date, 6)
    return data

@app.callback(Output('fault_type_bar', 'figure'),[
                Input('date-range_ft', 'end_date'),
                Input('FaultTrending', 'clickData'),
                Input('Last_month_fault', 'clickData'),
                Input('Last_6_months_fault', 'clickData'),
                Input('Last_month_fault_by_vobc', 'clickData'),
                Input('Last_6_months_fault_by_vobc', 'clickData'),
                ])
def update_fault_bar_trend(end_date, cd_1,cd_2,cd_3,cd_4,cd_5):
    data = {}
    tri = dash.callback_context.triggered[0]["prop_id"]
    if tri == 'FaultTrending.clickData':
        start_date= cd_1['points'][0]['x']
        data = mft.gen_fault_trend_bar(start_date,1)
        return data
    start_date = end_date
    if tri == 'Last_month_fault.clickData':
        fault_code = cd_2['points'][0]['x']
        data = mft.gen_fault_trend_bar(start_date,-1, fault_code)
        return data
    if tri == 'Last_6_months_fault.clickData':
        fault_code = cd_3['points'][0]['x']
        data = mft.gen_fault_trend_bar(start_date,-6, fault_code)
        return data
    if tri == 'Last_month_fault_by_vobc.clickData':
        vobc = cd_4['points'][0]['x']
        data = mft.gen_fault_trend_bar(start_date,-1, None, vobc)
        return data
    if tri == 'Last_6_months_fault_by_vobc.clickData':
        vobc = cd_5['points'][0]['x']
        data = mft.gen_fault_trend_bar(start_date,-1, None, vobc)
        return data
 
    
    return data


@app.callback(Output('vobc_fault_list', 'data'),[
                Input('fault_type_bar', 'clickData'),
                ])
def update_vobc_list(clickData):
    return _vobc_list(clickData)

def _vobc_list(clickData):
    if clickData is None:
        return []
    start_date = clickData['points'][0]['x']
    data = mft.gen_vobc_fault_list(start_date)
    return data