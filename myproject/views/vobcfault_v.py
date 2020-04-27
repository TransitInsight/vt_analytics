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
def create_fig_bar(fault_code, start_date, end_date):
    df_res = vobcfault_m.get_count_by(fault_code, start_date, end_date)
    
    df_list = []
    df_list.append(df_res[(df_res['VOBCID']<=150)].sort_values(by=['VOBCID']) )
    df_list.append(df_res[(df_res['VOBCID']>150)].sort_values(by=['VOBCID']) )

    fig = make_subplots(rows=2, cols=1, shared_yaxes=True)
    i = 1
    for df in df_list:
        j = 0
        for fault_code in sorted(df['faultCode'].unique()):
            df_fc = df[df['faultCode']==fault_code]
            fig.append_trace(go.Bar(
                    name=vobcfault_m.get_fault_name(fault_code), 
                    x=df_fc['VOBCID'], 
                    y=df_fc['FaultCount'], 
                    legendgroup=vobcfault_m.get_fault_name(fault_code), 
                    showlegend = i==1,
                    marker=dict(color=cfg.vobc_fault_color_dict[fault_code])
                    ), 
                    row=i, col=1)    
            j+=1
        i+=1

    y_max = df.groupby(['VOBCID']).sum().FaultCount.max() * 1.01

    if (type(start_date) is datetime):
        start_date = start_date.strftime("%Y-%m-%dT%H:%M:%S")
    if (type(end_date) is datetime):
        end_date = end_date.strftime("%Y-%m-%dT%H:%M:%S")

    #title_text = 'VOBC Fault Histogram ({} - {})'.format(start_date[0:10], end_date[0:10])
    fig.update_layout(barmode='stack', height=600, hovermode='closest',
        #legend=dict(x=-.1, y=0),
        #paper_bgcolor="LightSteelBlue", 
        #title = { 'text': title_text, 'font':{'size':20}, 'yanchor': 'top' },
        margin=dict(l=2, r=2, t=30, b=2))
    fig.update_xaxes(row=1,col=1, dtick = 4, title_text='vobc id')#, type='category')
    fig.update_xaxes(row=2,col=1, dtick = 4, title_text='vobc id')#, type='category')
    fig.update_yaxes(range=[0,y_max], title_text='fault count')

    return fig


def create_fig_area(fault_code, start_date, end_date, click_value):

    if (type(start_date) is datetime):
        start_date = start_date.strftime("%Y-%m-%dT%H:%M:%S")
    if (type(end_date) is datetime):
        end_date = end_date.strftime("%Y-%m-%dT%H:%M:%S")

    click_fault_code = -1
    click_vobcid = -1
    title = 'date'
    if (click_value != None):
        click_vobcid = click_value['points'][0]['x']
        click_fault_code = click_value['points'][0]['curveNumber'] + 1 #click curveNumber is between 0 and 14
        if (click_fault_code > 15) :
            click_fault_code -= 15
        fault_code = click_fault_code
        title = 'date (vobc={}, fault={})'.format(click_vobcid, fault_code)

    df = vobcfault_m.get_count_trend(fault_code, start_date, end_date, click_vobcid)
    y_max = df.groupby(['LoggedDate']).max().max() * 1.01
    fig = go.Figure()

    for fc_code in sorted(df['faultCode'].unique()):
        df_fc = df[df['faultCode']==fc_code]
        fig.add_trace(go.Scatter(x=df_fc['LoggedDate'], y=df_fc['FaultCount'],
            showlegend = False, 
            #fillcolor=cfg.vobc_fault_color_dict[fc_code],
            line_color=cfg.vobc_fault_color_dict[fc_code],
            stackgroup = 'one'
            )) 

    fig.update_layout(height=300, margin=dict(l=2, r=10, t=30, b=2), hovermode='closest')
    
    fig.update_xaxes(title_text=title)#, type='category')
    fig.update_yaxes(range=[0,y_max], title_text='fault count')

    return fig

#%%

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
                options=vobcfault_m.create_dropdown_options(),
                value=-1
            )
        ], style={'display':'inline-block', 'font-size':'120%', 'width': '300px', 'margin-top':'8px'})

    fg_div_bar = html.Div([
            dcc.Graph(id='fig_bar', figure=create_fig_bar(-1, filter_start_date, filter_end_date))], 
            style={'width':'100%', 'display':'inline-block'}
        )
    fg_div_area = html.Div([
            dcc.Graph(id='fig_area', figure=create_fig_area(-1, filter_start_date, filter_end_date, None))], 
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
                    dbc.Col(fg_div_bar, width = 8),
                    dbc.Col(fg_div_area, width = 4)
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
                            html.Pre(id='selectoutput_bar', style={'paddingTop':35})
                            ], style={'paddingTop':35})
                        ),
                    dbc.Col(
                        html.Div([
                            html.Pre(id='relayoutoutput_bar', style={'paddingTop':35})
                            ], style={'paddingTop':35})
                        ),
                    dbc.Col(
                        html.Div([
                            html.Pre(id='restyleoutput_bar', style={'paddingTop':35})
                            ], style={'paddingTop':35})
                        ),


                    dbc.Col(
                        html.Div([
                            html.Pre(id='clickoutput_area', style={'paddingTop':35})
                            ], style={'paddingTop':35})
                        ),
                    dbc.Col(
                        html.Div([
                            html.Pre(id='selectoutput_area', style={'paddingTop':35})
                            ], style={'paddingTop':35})
                        ),
                    dbc.Col(
                        html.Div([
                            html.Pre(id='relayoutoutput_area', style={'paddingTop':35})
                            ], style={'paddingTop':35})
                        ),
                    dbc.Col(
                        html.Div([
                            html.Pre(id='restyleoutput_area', style={'paddingTop':35})
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
def display_figure_bar(value, start_date, end_date):
    f = create_fig_bar(value, start_date, end_date)
    return f

@app.callback(
    Output('fig_area', 'figure'),
    [
        Input('app-1-dropdown', 'value'),
        Input('my_date_picker', 'start_date'),
        Input('my_date_picker', 'end_date') ,
        Input('fig_bar', 'clickData')

    ])
def display_figure_area(value, start_date, end_date, click_value):
    f = create_fig_area(value, start_date, end_date, click_value)
    return f

#####----------------------------------------------------
@app.callback(
    Output('clickoutput_bar', 'children'),
    [
        Input('fig_bar', 'clickData')
    ])
def clicked_bar_data(value):
    return 'click: ' + json.dumps(value, indent=2)


@app.callback(
    Output('selectoutput_bar', 'children'),
    [
        Input('fig_bar', 'selectedData')
    ])
def select_bar_data(value):
    return 'select : ' +json.dumps(value, indent=2)

@app.callback(
    Output('relayoutoutput_bar', 'children'),
    [
        Input('fig_bar', 'relayoutData')
    ])
def relayout_bar_data(value):
    return 'relayout :' + json.dumps(value, indent=2)

@app.callback(
    Output('restyleoutput_bar', 'children'),
    [
        Input('fig_bar', 'restyleData')
    ])
def restyle_bar_data(value):
    return 'restyle:' + json.dumps(value, indent=2)



@app.callback(
    Output('clickoutput_area', 'children'),
    [
        Input('fig_area', 'clickData')
    ])
def clicked_area_data(value):
    return 'click : ' + json.dumps(value, indent=2)


@app.callback(
    Output('selectoutput_area', 'children'),
    [
        Input('fig_area', 'selectedData')
    ])
def select_area_data(value):
    return 'select :' + json.dumps(value, indent=2)


@app.callback(
    Output('relayoutoutput_area', 'children'),
    [
        Input('fig_area', 'relayoutData')
    ])
def relayout_area_data(value):
    return 'relayout: ' + json.dumps(value, indent=2)


@app.callback(
    Output('restyleoutput_area', 'children'),
    [
        Input('fig_area', 'restyleData')
    ])
def restyle_area_data(value):
    return 'restyle:' + json.dumps(value, indent=2)
