import dash_core_components as dcc
import dash_html_components as html
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
filter_end_date = dt(2015, 4, 1)


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
    df = module_vobcfault.get_faultcount_by_vobcid_loc(start_date, end_date)
    
    if df is None:
        pass

    data_1 = [gen_scatter_graph_data(df,"locationName", "vobcid", 5000)]          
    data_1
    return{'data': data_1,                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 
            'layout' : go.Layout(title = "Faults by VOBCID and LOCATION", 
                xaxis = {'title': 'Location'},
                yaxis = {'title': 'VOBCID'}, 
                hovermode="closest",
                clickmode =  'event+select')
            }

def gen_bar_data(df):
    datax = df.index.tolist()
    datay = df['FaultCount'].tolist()
    fig = go.Bar(x=datax, y=datay)
    return fig


checkboxdict = module_vobcfault.create_dropdown_options()

def b_display_click_data(clickData, faultcode_, start_date, end_date, df):
    #df1 = order_data.sort_Dates(df, start_date, end_date)
    #df1 = df[df['Fault Code'].isin(faultcode_)]
    if clickData is None:
        vobcid_ = 240
        location = 'GRE-DEB'
    else:
        vobcid_= clickData['points'][0]['y']
        location = clickData['points'][0]['x']

    if df is None:
        pass

    data_1 = [gen_bar_data(df)]

    return{'data': data_1,                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 
            'layout' : go.Layout(title = "Faults by Date VOBCID: {} Location: {}".format(vobcid_, location), 
                xaxis = {'title': 'Date'},
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
        )], className = "six columns"),
        
        html.Div([
            dcc.Graph(id = 'BarGraph', 
                #style={ 'float': 'left', "display":"block", "height" : "35vh",'width': "75vw"},
                
            ),
        ], className = "six columns"),

    html.Div(id='app-2-display-value'),
      html.Div([    
        html.Div([
            dcc.Graph(id = 'Scatterplot', 
                style={ 'float': 'left', "display":"block", "height" : "60vh",'width': "75vw"},
            
            ),
        ], className = "six columns"),

        html.Div([
            html.Br(),
            html.Br(),
            html.Br(),
            html.Br(),
            html.Br(),
            html.Br(),
            dcc.Checklist(
                id = 'Checklist',
                options= checkboxdict,
                value=  [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15],
                style={'float': 'right', "height" : "40vh",'width': "20vw"}, 
                labelStyle={'display': 'block'}
            )
        ], className = "six columns")

        


    ],className="row"),
])

def display_click_data_bar(clickData, faultcode_, start_date, end_date):
    df = module_vobcfault.get_count_by(faultcode_, start_date, end_date)
    return b_display_click_data(clickData, faultcode_, start_date, end_date, df)
 

@app.callback(
    Output('app-2-display-value', 'children'),
    [Input('app-2-dropdown', 'value')])
def display_value(clicked_date):
    return 'You have selected in app2 "{}"'.format(clicked_date)

@app.callback(
    Output('BarGraph', 'figure'),[
    Input('Scatterplot', 'clickData'),
    Input('Checklist', 'value'),
    Input('date-range', 'start_date'),
    Input('date-range', 'end_date')])
def display_click_data(clickData, faultcode_ = 3, start_date = filter_start_date, end_date = filter_end_date ):
    # df = module_vobcfault.get_count_by(faultcode_, start_date, end_date)
    # return b_display_click_data(clickData, faultcode_, start_date, end_date, df)
    return display_click_data_bar(clickData, faultcode_, start_date, end_date)


@app.callback(Output('Scatterplot', 'figure'),
                [Input('Checklist', 'value'),
                Input('date-range', 'start_date'),
                Input('date-range', 'end_date')])
def update_Scatter(faultcode_ = 3,start_date = filter_start_date ,end_date = filter_end_date):
    return _update_Scatter(faultcode_,start_date,end_date)
    


if __name__ == "__main__":
    app.run_server()
  

