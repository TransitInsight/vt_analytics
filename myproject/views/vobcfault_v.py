#%%
import json
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
from datetime import datetime
from datetime import timedelta

from app import app

from myproject.models import vobcfault_m
import myproject.config as cfg
import pandas as pd
import plotly.graph_objs as go
from plotly.subplots import make_subplots

#%%


filter_start_date = datetime(2015, 1, 1)
filter_end_date = datetime.today()

#%%
def create_fig_bar(fault_name, start_date, end_date):
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
                    legendgroup=fault_code, showlegend = i==1, marker=dict(color=cfg.vobc_fault_color_dict[fault_code[:2]])
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
    fig.update_layout(barmode='stack', height=600, hovermode='closest',
        #paper_bgcolor="LightSteelBlue", 
        #title = { 'text': title_text, 'font':{'size':20}, 'yanchor': 'top' },
        margin=dict(l=2, r=2, t=30, b=2))
    fig.update_xaxes(row=1,col=1, dtick = 4, title_text='vobc id')#, type='category')
    fig.update_xaxes(row=2,col=1, dtick = 4, title_text='vobc id')#, type='category')
    fig.update_yaxes(range=[0,y_max], title_text='fault count')

    return fig


def create_fig_area(fault_name, start_date, end_date):

    if (type(start_date) is datetime):
        start_date = start_date.strftime("%Y-%m-%dT%H:%M:%S")
    if (type(end_date) is datetime):
        end_date = end_date.strftime("%Y-%m-%dT%H:%M:%S")

    df = vobcfault_m.get_count_trend(fault_name, start_date, end_date)
    y_max = df.groupby(['LoggedDate']).max().max() * 1.01
    fig = go.Figure()

    for fault_code in sorted(df['faultName'].unique()):
        df_fc = df[df['faultName']==fault_code]
        fig.add_trace(go.Scatter(x=df_fc['LoggedDate'], y=df_fc['FaultCount'],
            showlegend = False, 
            fillcolor=cfg.vobc_fault_color_dict[fault_code[:2]],
            line_color=cfg.vobc_fault_color_dict[fault_code[:2]],
            stackgroup = 'one'
            )) 

    fig.update_layout(height=600, margin=dict(l=2, r=2, t=30, b=2), hovermode='closest')
    fig.update_xaxes(title_text='date')#, type='category')
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

    fg_div_bar = html.Div([
            dcc.Graph(id='fig_bar', figure=create_fig_bar('00. All', filter_start_date, filter_end_date))], 
            style={'width':'100%', 'display':'inline-block'}
        )
    fg_div_area = html.Div([
            dcc.Graph(id='fig_area', figure=create_fig_area('00. All', filter_start_date, filter_end_date))], 
            style={'width':'100%', 'display':'inline-block'}
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
            dbc.Row(
                [
                    dbc.Col(fg_div_bar, width = 6),
                    dbc.Col(fg_div_area, width = 6)
                ]
            ),
            dbc.Row(
                [
                    dbc.Col(
                        html.Div([
                            html.Pre(id='clickoutput_bar', style={'paddingTop':35})
                            ], style={'paddingTop':35})
                        ),
                    dbc.Col(
                        html.Div([
                            html.Pre(id='clickoutput_area', style={'paddingTop':35})
                            ], style={'paddingTop':35})
                        )
                ]
            )
        ]
    )
    return retDiv


#%%
layout = create_layout()

@app.callback(
    Output('fig_bar', 'figure'),
    [
        Input('app-1-dropdown', 'value'),
        Input('my_date_picker', 'start_date'),
        Input('my_date_picker', 'end_date') 
    ])
def display_figure(value, start_date, end_date):
    f = create_fig_bar(value, start_date, end_date)
    return f

@app.callback(
    Output('fig_area', 'figure'),
    [
        Input('app-1-dropdown', 'value'),
        Input('my_date_picker', 'start_date'),
        Input('my_date_picker', 'end_date') 
    ])
def display_figure(value, start_date, end_date):
    f = create_fig_area(value, start_date, end_date)
    return f

@app.callback(
    Output('clickoutput_bar', 'children'),
    [
        Input('fig_bar', 'clickData')
    ])
def clicked_bar_data(value):
    return json.dumps(value, indent=2)


@app.callback(
    Output('clickoutput_area', 'children'),
    [
        Input('fig_area', 'clickData')
    ])
def clicked_area_data(value):
    return json.dumps(value, indent=2)
