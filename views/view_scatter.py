import dash_core_components as dcc
import dash_html_components as html
import dash_table
from dash.dependencies import Input, Output
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
from datetime import datetime as dt
import re

from modules import module_vobcfault
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
                xaxis = {'title': 'Location'},
                yaxis = {'title': 'VOBCID'}, 
                dragmode = False, 
                hovermode="closest",
                clickmode =  'event+select')
            }


def gen_bar_data(df):
    datax = df['date'].tolist()
    datay = df['FaultCount'].tolist()
    fig = go.Bar(x=datax, y=datay)
    return fig

checkboxdict = module_vobcfault.create_dropdown_options()

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
            style={ 'float': 'left', "display":"block", 'height': '3vw', 'width': "20vw"}
        ),
        dcc.Dropdown(
                id = 'fault_code',
                options= checkboxdict,
                value = -1,
                style={ 'float': 'left', "display":"block",'height': '3vw','width': "50vw"},
            )
        ], ),
        
      html.Div([    
        
            dcc.Graph(id = 'Scatterplot',  
                style={ 'float': 'left', "display":"block", "height" : "65vh",'width': "60vw"},
            ),
            dcc.Graph(id = 'BarGraph', 
                style={ 'float': 'left', "display":"block", "height" : "33vh",'width': "38vw"},  
            ),
        

    ])
])


@app.callback(
    Output('BarGraph', 'figure'),[
    Input('Scatterplot', 'clickData'),
    Input('fault_code', 'value'),
    Input('date-range', 'start_date'),
    Input('date-range', 'end_date')])
def display_click_data(clickData, faultcode_ , start_date , end_date ):
    return _display_click_data(clickData, start_date, end_date, faultcode_ )


@app.callback(Output('Scatterplot', 'figure'),
                [Input('fault_code', 'value'),
                Input('date-range', 'start_date'),
                Input('date-range', 'end_date')])
def update_Scatter(faultcode_,start_date,end_date):
    
    return _update_Scatter(faultcode_,start_date,end_date)
    


if __name__ == "__main__":
    app.run_server()
  

