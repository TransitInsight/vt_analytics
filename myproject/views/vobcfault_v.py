#%%
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
from datetime import datetime
from datetime import timedelta

from app import app

from myproject.models import vobcfault_m
import pandas as pd
import plotly.graph_objs as go
from plotly.subplots import make_subplots
import plotly.io as pio

#%%

'''Default template: 'plotly'
Available templates:
    ['ggplot2', 'seaborn', 'simple_white', 'plotly',
        'plotly_white', 'plotly_dark', 'presentation', 'xgridoff',
        'ygridoff', 'gridon', 'none']'''
pio.templates.default = "simple_white"

#%%

filter_start_date = datetime(2015, 1, 1)
filter_end_date = datetime.today()

color_dict = {
    '00': "#074263", 
    '01': "#0B5394", 
    '02': "#3D85C6", 
    '03': "#6D9EEB", 
    '04': "#A4C2F4",
    '05': "#CFE2F3", 
    '06': "#5B0F00", 
    '07': "#85200C", 
    '08': "#A61C00", 
    '09': "#CC4125", 
    '10': "#DD7E6B", 
    '11': "#E6B8AF", 
    '12': "#F8CBAD", 
    '13': "#F4CCCC", 
    '14': "#274E13", 
    '15': "#38761D", 
    '16': "#E06666", 
    '17': "#CC0000", 
    '18': "#20124D"}

#%%
def create_fig(fault_name, start_date, end_date):
    df_res = vobcfault_m.get_count_by(fault_name, start_date, end_date)
    
    df_list = []
    df_list.append(df_res[(df_res['VOBCID']<=150)].sort_values(by=['VOBCID']) )
    df_list.append(df_res[(df_res['VOBCID']>150)].sort_values(by=['VOBCID']) )

    fig = make_subplots(rows=2, cols=1, shared_yaxes=True)
    i = 1
    for df in df_list:
        j = 0
        for fault_code in sorted(df['faultName'].unique()):
            df_fc = df[df['faultName']==fault_code]
            fig.append_trace(go.Bar(
                    name=fault_code, x=df_fc['VOBCID'], y=df_fc['FaultCount'], 
                    legendgroup=fault_code, showlegend = i==1, marker=dict(color=color_dict[fault_code[:2]])
                    ), 
                    row=i, col=1)    
            j+=1
        i+=1

    y_max = df_res.groupby(['VOBCID']).sum().max()[0] * 1.02

    if (type(start_date) is datetime):
        start_date = start_date.strftime("%Y-%m-%dT%H:%M:%S")
    if (type(end_date) is datetime):
        end_date = end_date.strftime("%Y-%m-%dT%H:%M:%S")

    #title_text = 'VOBC Fault Histogram ({} - {})'.format(start_date[0:10], end_date[0:10])
    fig.update_layout(barmode='stack', height=600, 
        #paper_bgcolor="LightSteelBlue", 
        #title = { 'text': title_text, 'font':{'size':20}, 'yanchor': 'top' },
        margin=dict(l=20, r=20, t=50, b=20))
    fig.update_xaxes(row=1,col=1, dtick = 4, title_text='vobc id')#, type='category')
    fig.update_xaxes(row=2,col=1, dtick = 4, title_text='vobc id')#, type='category')
    fig.update_yaxes(range=[0,y_max], title_text='fault count')

    return fig

#%%

def create_dropdown_options():
    df_res = vobcfault_m.get_all_fault()

    fc_options = [{'label':x, "value":x} for x in df_res['faultName'].unique()]
    fc_options.insert(0,{'label':'00. All','value':'00. All'})

    return fc_options

def create_layout():
    

    date_div = html.Div([
            dcc.DatePickerRange(
                id='my_date_picker',
                min_date_allowed=datetime(2014, 1, 1),
                max_date_allowed=datetime.today() + timedelta(days=1),
                start_date=filter_start_date,
                end_date=filter_end_date
            )
        ], style={'display':'inline-block', 'font_size': '200%', 'width':'300px'})

    fault_name_div = html.Div([
            dcc.Dropdown(
                id='app-1-dropdown',
                options=create_dropdown_options(),
                value='00. All'
            )
        ], style={'display':'inline-block', 'font-size':'120%', 'width': '300px', 'margin-top':'8px'})

    fg_div = html.Div([
            dcc.Graph(id='plot', figure=create_fig('00. All', filter_start_date, filter_end_date))], 
            style={'width':'40%', 'display':'inline-block'}
        )

    retDiv = html.Div(
        [
            dbc.Row(
                [
                    dbc.Col(html.Div("Date Range : ", style={'margin-top':'12px', 'font-size':'120%'}), width='auto'),
                    dbc.Col(date_div, width='auto'),
                    dbc.Col(html.Div("VOBC Fault : ", style={'margin-top':'12px', 'font-size':'120%'}), width='auto'),
                    dbc.Col(fault_name_div, width='auto'),
                ]
            ),
            dbc.Row(dbc.Col(fg_div)),
        ]
    )
    return retDiv


#%%
layout = create_layout()

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