#%%
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
from datetime import datetime
from datetime import timedelta

from app import app

from myproject.models import vobcfault_m
import pandas as pd
import plotly.graph_objs as go
from plotly.subplots import make_subplots

#%%


#%%

filter_start_date = datetime(2015, 1, 1)
filter_end_date = datetime.today()

color_dict = {
    0: "#074263", 
    1: "#0B5394", 
    2: "#3D85C6", 
    3: "#6D9EEB", 
    4: "#A4C2F4",
    5: "#CFE2F3", 
    6: "#5B0F00", 
    7: "#85200C", 
    8: "#A61C00", 
    9: "#CC4125", 
    10: "#DD7E6B", 
    11: "#E6B8AF", 
    12: "#F8CBAD", 
    13: "#F4CCCC", 
    14: "#274E13", 
    15: "#38761D", 
    16: "#E06666", 
    17: "#CC0000", 
    18: "#20124D"}

#%%
def create_fig(fault_name, start_date, end_date):
    df_res = vobcfault_m.get_count_by(fault_name, start_date, end_date)
    
    df_list = []
    df_list.append(df_res[(df_res['VOBCID']<=150)] )
    df_list.append(df_res[(df_res['VOBCID']>150)] )

    fig = make_subplots(rows=2, cols=1, shared_yaxes=True)
    i = 1
    for df in df_list:
        j = 0
        for fault_code in sorted(df['faultName'].unique()):
            df_fc = df[df['faultName']==fault_code]
            fig.append_trace(go.Bar(
                    name=fault_code, x=df_fc['VOBCID'], y=df_fc['FaultCount'], 
                    legendgroup=fault_code, showlegend = i==1,
                    marker=dict(color=color_dict[j])
                    ), 
                    row=i, col=1)    
            j+=1
        i+=1

    y_max = df_res.groupby(['VOBCID']).sum().max()[0] * 1.02
    fig.update_layout(barmode='stack', height=700, paper_bgcolor="LightSteelBlue")
    fig.update_yaxes(range=[0,y_max])
    return fig

#%%

def create_dropdown_options():
    df_res = vobcfault_m.get_all_fault()

    fc_options = []
    fc_options.append({'label':'00. All','value':'00. All'})
    for fc in df_res['faultName'].unique():
        fc_options.append({'label':fc,'value':fc})
    return fc_options


#%%
layout = html.Div([
    html.H3('VOBC Fault'),

    html.Div([
        dcc.DatePickerRange(
            id='my_date_picker',
            min_date_allowed=datetime(2014, 1, 1),
            max_date_allowed=datetime.today() + timedelta(days=1),
            start_date=filter_start_date,
            end_date=filter_end_date
        )
    ], style={'display':'inline-block', 'width': '30%'}),

    html.Div([
        dcc.Dropdown(
            id='app-1-dropdown',
            options=create_dropdown_options(),
            value='00. All'
        )
    ], style={'display':'inline-block', 'width': '30%'}),

    html.Div(id='app-1-display-value'),
    dcc.Link('Go to App 2', href='/views/view2'),

    html.Div([
        dcc.Graph(id='plot', figure=create_fig('00. All', filter_start_date, filter_end_date))], 
        style={'width':'80%', 'display':'inline-block'}
    )
])

@app.callback(
    Output('app-1-display-value', 'children'),
    [Input('app-1-dropdown', 'value'),
     Input('my_date_picker', 'start_date'),
     Input('my_date_picker', 'end_date') 
    ])
def display_value(value, start_date, end_date):
    return 'You have selected in app1: "{}" start = {}, end={}'.format(value, start_date, end_date)

@app.callback(
    Output('plot', 'figure'),
    [
        Input('app-1-dropdown', 'value'),
        Input('my_date_picker', 'start_date'),
        Input('my_date_picker', 'end_date') 
    ])
def display_figure(value, start_date, end_date):
    f = create_fig(value, start_date, end_date)
    return f