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
from views.ViewTrainmoveClass import ViewTrainmoveClass
from views.ViewFaultListClass import ViewFaultListClass
import util as util


filter_start_date = dt(2015, 1, 1)
filter_end_date = dt(2020, 1, 1)
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

def checkfaultcode(faultcode):
    if faultcode is None:
        faultcode = -1
    return faultcode

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
    FaultCount = df["FaultCount"].tolist()
    FaultCount = np.array(FaultCount)
    data = gen_scatter_graph(df, datax, datay, "FaultCount", FaultCount, size_scale)   
    return data


def gen_bar_data(df):
    datax = df['date'].tolist()
    datay = df['FaultCount'].tolist()
    fig = go.Bar(x=datax, y=datay)
    return fig

checkboxdict = module_vobcfault.create_dropdown_options()


def create_fig_fault_list(table_id, fault_code, start_date, end_date, vobc_id):
    c = ViewFaultListClass(table_id, fault_code, start_date, end_date, vobc_id)
    c.create_fig()
    return c.get_fig()

def create_fig_by_trainmove(vobc_id, op_date, fault_code, offset=0):
    c = ViewTrainmoveClass(vobc_id, op_date, fault_code, offset)
    c.create_fig()
    return c.get_fig()

app.layout = html.Div([

])
layout = html.Div([

    html.Div([
        dcc.DatePickerRange(
            id='date-range',
            min_date_allowed=filter_start_date,
            max_date_allowed=filter_end_date,
            initial_visible_month=filter_start_date,
            end_date=filter_end_date,
            style={ 'display':'inline-block', 'font_size': '100%', 'width':'300px', 'margin-top': '2px'}
        ),
        dcc.Dropdown(
                id = 'fault_code',
                options= checkboxdict,
                value = -1,
                style={ 'display':'inline-block', 'font-size':'110%', 'width': '300px', 'margin-top':'8px'},
            )
        ], ),
        
    html.Div([    
        
            dcc.Graph(id = 'Scatterplot',  
                style={ 'float': 'left', "display":"block", "height" : "65vh",'width': "60vw"},
                
            ),
            dcc.Graph(id = 'BarGraph', 
                style={ 'float': 'right', "display":"block", "height" : "33vh",'width': "38vw"},  
            ),

            html.Div([create_fig_fault_list('fig_list_dates', -1, filter_start_date, filter_end_date, -1)],
            style={ 'float': 'right', "display":"block", "height" : "33vh",'width': "38vw"} 
            )
            ]),

    html.Div([
                dcc.Graph(id='fig_by_trainmove_vs', figure=create_fig_by_trainmove(112, '2015-7-3 10:51', 3),
                style={ 'float': 'left', "display":"block", "height" : "30vh",'width': "98vw"} 
                 ),
                html.Button('<<', id='vs_button_prev_page'),
                html.Button('<', id='vs_button_prev'),
                html.Button('>', id='vs_button_next'),
                html.Button('>>', id='vs_button_next_page')
                
            ],style={'width':'100%', 'display':'inline-block'}, 
        ),

    dcc.Store(id='vs_session_store')
           
             
        

    ])



@app.callback(
    Output('BarGraph', 'figure'),[
    Input('Scatterplot', 'clickData'),
    Input('fault_code', 'value'),
    Input('date-range', 'start_date'),
    Input('date-range', 'end_date')])
def display_click_data(clickData, faultcode_ , start_date , end_date ):
    return _display_click_data(clickData, start_date, end_date, faultcode_ )

def _display_click_data(clickData, start_date, end_date, faultcode_):
    if clickData is None:
        vobcid_ = 240
        location = 'GRE-DEB'
    else:
        vobcid_= clickData['points'][0]['y']
        location = clickData['points'][0]['x']

    start_date,end_date = datecheck(start_date, end_date)
    faultcode_ = checkfaultcode(faultcode_)
    
    df = module_vobcfault.get_faultcount_by_vobcid_loc_date(start_date, end_date, vobcid_, faultcode_)
    
    if len(df.index) == 0:
        data_1 = []
    else:
        data_1 = [gen_bar_data(df)]

    return{'data': data_1,                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 
            'layout' : go.Layout(title = "Faults by Date VOBCID: {} Location: {}".format(vobcid_, location), 
                xaxis = {'title': 'Date' },
                dragmode = False,
                yaxis = {'title': 'Faultcount'}, 
                hovermode="closest")
            }

@app.callback(Output('Scatterplot', 'figure'),
                [Input('fault_code', 'value'),
                Input('date-range', 'start_date'),
                Input('date-range', 'end_date')])
def update_Scatter(faultcode_,start_date,end_date):
    
    return _update_Scatter(faultcode_,start_date,end_date)

def _update_Scatter(faultcode_, start_date,end_date):
    start_date,end_date = datecheck(start_date, end_date)
    faultcode_ = checkfaultcode(faultcode_)

    df = module_vobcfault.get_faultcount_by_vobcid_loc(start_date, end_date, faultcode_)
    
    if len(df.index) == 0:
        data_1 = []
    else:
        data_1 = [gen_scatter_graph_data(df,"locationName", "vobcid", 5000)]          
   
    return{'data': data_1,                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 
            'layout' : go.Layout(title = "Faults by VOBCID and LOCATION", 
                xaxis = {'title': 'Location', 'categoryorder' : 'category ascending'},
                yaxis = {'title': 'VOBCID'}, 
                dragmode = False, 
                hovermode="closest",
                clickmode =  'event+select')
            }
    
@app.callback(
    Output('fig_list_dates', 'data'),
    [
        Input('fault_code', 'value'),
        Input('date-range', 'start_date'),
        Input('date-range', 'end_date') ,
        Input('Scatterplot', 'clickData'),
        Input('BarGraph', 'clickData')
        
    ])
def display_figure_fault_list_callback(faultcode_, start_date, end_date, fault_click_value, trend_click_value):
    start_date,end_date = datecheck(start_date, end_date)
    faultcode_ = checkfaultcode(faultcode_)
    return display_figure_fault_list(faultcode_, start_date, end_date, fault_click_value, trend_click_value)

def display_figure_fault_list(value, start_date, end_date, fault_click_value, trend_click_value):    

    fault_code = value
    click_fault_code = -1
    click_vobcid = -1
    if (fault_click_value != None):
        click_vobcid = fault_click_value['points'][0]['y']
        click_fault_code = fault_click_value['points'][0]['curveNumber'] + 1 #click curveNumber is between 0 and 14
        if (click_fault_code > 15) :
            click_fault_code -= 15
        if (fault_code == -1): #if not -1, the dropdown only selected one Fault, so the click must be on the same fault, no need to change
            fault_code = click_fault_code

    op_date = None
    if trend_click_value != None:
        op_date = trend_click_value['points'][0]['x']
        start_date = util.str2date1(op_date)
        end_date = start_date + timedelta(days = 1)

    c = ViewFaultListClass('fig_list_dates', -1, start_date, end_date, click_vobcid)
    d = c.get_data()

    return d

@app.callback(Output('vs_session_store', 'data'),
              [
                  Input('vs_button_prev_page', 'n_clicks'),
                  Input('vs_button_prev', 'n_clicks'),
                  Input('vs_button_next', 'n_clicks'),
                  Input('vs_button_next_page', 'n_clicks'),
                  Input('Scatterplot', 'clickData'),
                  Input('BarGraph', 'clickData'),
                  Input('fig_list_dates', 'active_cell')
              ],
              [State('vs_session_store', 'data')])
def update_offset_callback( prev_page, prev, next, next_page, first_value, second_value, thrid_value, data):

    if any ('button' in item['prop_id'] for item in dash.callback_context.triggered): #not triggerred by button, it must be triggerred by others, reset offset
        return update_offset(dash.callback_context.triggered, data)
    else:
        return {'offset': 0}

def update_offset(triggeredItems, data):    
    data = data or {'offset': 0}
    offset = 0

    if any ('vs_button_prev_page.n_clicks' == item['prop_id'] for item in triggeredItems):
        offset = -2
    elif any ('vs_button_next_page.n_clicks' == item['prop_id'] for item in triggeredItems):
        offset = 2
    elif any ('vs_button_prev.n_clicks' == item['prop_id'] for item in triggeredItems):
        offset = -1
    elif any ('vs_button_next.n_clicks' == item['prop_id'] for item in triggeredItems):
        offset = 1

    data['offset'] = data['offset'] + offset #-prev_page * 2 - prev + next + 2*next_page

    return data

@app.callback(
    Output('fig_by_trainmove_vs', 'figure'),
    #Output('clickoutput_bar', 'children'),
    [
        Input('Scatterplot', 'clickData'),
        Input('BarGraph', 'clickData'),
        Input('fig_list_dates', 'active_cell'),
        Input('fig_list_dates', 'derived_viewport_data'),
        Input('vs_session_store', 'data')
    ]
    )
def display_figure_trainmove_callback(first_value, second_value, table_active_cell, table_data, timewindow_value):
    return display_figure_trainmove(first_value, second_value, table_active_cell, table_data, timewindow_value)

def display_figure_trainmove(first_value, second_value, table_active_cell, table_data, timewindow_value):
    vobc_id = None
    fault_code = None
    if first_value != None:
        vobc_id = first_value['points'][0]['y']
        fault_code = first_value['points'][0]['curveNumber'] + 1 #click curveNumber is between 0 and 14
        if (fault_code > 15) :
            fault_code -= 15

    op_date = None
    if second_value != None:
        op_date = second_value['points'][0]['x']

    offset = 0
    if timewindow_value != None:
        offset = timewindow_value['offset']

    delta = timedelta(hours=offset/2)

    if table_data is not None and len(table_data) != 0 and table_active_cell is not None and len(table_data) > table_active_cell['row']:
        op_date = table_data[table_active_cell['row']]['loggedAt']

    f = create_fig_by_trainmove(vobc_id, op_date, fault_code, delta)
    return f
if __name__ == "__main__":
    app.run_server()
  

