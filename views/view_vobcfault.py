import os,sys,inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir) 


#%%
import json
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
from datetime import datetime
from datetime import timedelta

from app import app

from modules import module_vobcfault as vobcfault_m
from modules import module_trainmove as trainmove_m
import config as cfg
import util as util
import pandas as pd
import plotly.graph_objs as go
from plotly.subplots import make_subplots

#%%


filter_start_date = datetime(2015, 1, 1)
filter_end_date = datetime(2015, 4, 1)

#%%
def create_fig_by_vobc(fault_code, start_date, end_date):
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
            fig.add_trace(go.Bar(
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

    start_date, end_date = util.date2str2(start_date, end_date)

    fig.update_layout(barmode='stack', height=600, hovermode='closest',
        margin=dict(l=2, r=2, t=30, b=2))
    fig.update_xaxes(row=1,col=1, dtick = 4, title_text='vobc id')#, type='category')
    fig.update_xaxes(row=2,col=1, dtick = 4, title_text='vobc id')#, type='category')
    fig.update_yaxes(range=[0,y_max], title_text='fault count')

    return fig


def create_fig_by_trend(fault_code, start_date, end_date, vobc_id):

    start_date, end_date = util.date2str2(start_date, end_date)

    title = 'vobc={}, fault={}'.format(vobc_id, fault_code)

    fig = make_subplots(rows=2, cols=1)
    df = vobcfault_m.get_count_trend(fault_code, start_date, end_date, vobc_id)
    if (not df.empty):
        y_max = df.groupby(['LoggedDate']).max().max() * 1.01
    
        for fc_code in sorted(df['faultCode'].unique()):
            df_fc = df[df['faultCode']==fc_code]
            fig.add_trace(go.Scatter(x=df_fc['LoggedDate'], y=df_fc['FaultCount'],
                showlegend = False, 
                line_color=cfg.vobc_fault_color_dict[fc_code],
                stackgroup = 'one'
                ),
                row=1,col=1) 
        fig.update_xaxes(row = 1, col = 1, title_text=title)#, type='category')
        fig.update_yaxes(row = 1, col = 1, range=[0,y_max], title_text='fault count by date')

    df = vobcfault_m.get_count_location(fault_code, start_date, end_date, vobc_id)
    if (not df.empty):
        y_max = df.groupby(['LocationName']).max().max() * 1.01
    
        for fc_code in sorted(df['faultCode'].unique()):
            df_fc = df[df['faultCode']==fc_code]
            fig.add_trace(go.Bar(x=df_fc['LocationName'], y=df_fc['FaultCount'],
                showlegend = False, 
                marker=dict(color=cfg.vobc_fault_color_dict[fault_code])
                ),
                row=2,col=1) 
        fig.update_xaxes(row = 2, col = 1, title_text=title)#, type='category')
        fig.update_yaxes(row = 2, col = 1, range=[0,y_max], title_text='fault count by location')
        
    fig.update_layout(barmode='stack')#, row = 2, col = 1)
    fig.update_layout(height=600, margin=dict(l=2, r=10, t=30, b=2), hovermode='closest')

    return fig

def set_fault_color(faultCode):
    return cfg.vobc_fault_color_dict[faultCode]

def create_fig_by_trainmove(vobc_id, op_date, fault_code):
    fig = go.Figure()

    if (vobc_id is None or op_date is None or fault_code is None):
        return fig

    op_date = util.str2date1(op_date)
    if (op_date is None):
        return fig
    first_fault_time = vobcfault_m.get_first_fault_time(op_date, fault_code, vobc_id)

    if (first_fault_time != None):
        start = first_fault_time - timedelta(minutes=5)
    else:
        start = op_date + timedelta(hours=6)
    end = start + timedelta(hours=1)    

    df = trainmove_m.get_trainmove(vobc_id, start, end)
    if (df.empty):
        return fig

    fig.add_trace(go.Scatter(x=df['loggedAt'], y=df['velocity'],
            name = "Actual Velocity",
            text='Actual Velocity = ' + df['velocity'].astype(str),
            line_color="goldenrod"
            )) 

    fig.add_trace(go.Scatter(x=df['loggedAt'], y=df['maximumVelocity'],
            name = "Max Velocity",
            text='Max Velocity = ' + df['maximumVelocity'].astype(str),
            line_color="green"
            )) 
    title = "Velocity (VOBC={})".format(vobc_id)

    df_fc = vobcfault_m.get_fault_list(start,end,vobc_id)
    if (df_fc.empty):
        return
    fig.add_trace(go.Scatter(x=df_fc['loggedAt'], y=df_fc['velocity'], 
            name="Vobc Fault",
            #hover_name = "faultCode",
            text='Fault = ' + df_fc['faultName'],
            mode='markers', marker=dict(size=15, 
                                        symbol='x',
                                        color=list(map(set_fault_color, df_fc['faultCode']))
                                        )
            ))
    fig.update_yaxes(title_text=title, showspikes=True)
    fig.update_xaxes(showspikes=True)
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
                id='fault-dropdown',
                options=vobcfault_m.create_dropdown_options(),
                value=-1
            )
        ], style={'display':'inline-block', 'font-size':'120%', 'width': '300px', 'margin-top':'8px'})

    fg_div_by_fault = html.Div([
            dcc.Graph(id='fig_by_fault', figure=create_fig_by_vobc(-1, filter_start_date, filter_end_date))], 
            style={'width':'100%', 'display':'inline-block'}
        )
    fg_div_by_trend = html.Div([
            dcc.Graph(id='fig_by_trend', figure=create_fig_by_trend(-1, filter_start_date, filter_end_date, -1))], 
            style={'width':'100%', 'display':'inline-block'}
        )
    fg_div_by_trainmove = html.Div([
            dcc.Graph(id='fig_by_trainmove', figure=create_fig_by_trainmove(112, '2015-7-3 10:51', 3))], 
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
                    dbc.Col(fg_div_by_fault, width = 8),
                    dbc.Col(fg_div_by_trend, width = 4)
                ]
            ),
            dbc.Row(
                [
                    dbc.Col(fg_div_by_trainmove, width = 12),
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
    Output('fig_by_fault', 'figure'),
    [
        Input('fault-dropdown', 'value'),
        Input('my_date_picker', 'start_date'),
        Input('my_date_picker', 'end_date') 
    ])
def display_figure_bar(value, start_date, end_date):
    f = create_fig_by_vobc(value, start_date, end_date)
    return f

@app.callback(
    Output('fig_by_trend', 'figure'),
    [
        Input('fault-dropdown', 'value'),
        Input('my_date_picker', 'start_date'),
        Input('my_date_picker', 'end_date') ,
        Input('fig_by_fault', 'clickData')

    ])
def display_figure_area(value, start_date, end_date, click_value):
    fault_code = value
    click_fault_code = -1
    click_vobcid = -1
    if (click_value != None):
        click_vobcid = click_value['points'][0]['x']
        click_fault_code = click_value['points'][0]['curveNumber'] + 1 #click curveNumber is between 0 and 14
        if (click_fault_code > 15) :
            click_fault_code -= 15
        if (fault_code == -1): #if not -1, the dropdown only selected one Fault, so the click must be on the same fault, no need to change
            fault_code = click_fault_code

    f = create_fig_by_trend(fault_code, start_date, end_date, click_vobcid)
    return f

@app.callback(
    Output('fig_by_trainmove', 'figure'),
    #Output('clickoutput_bar', 'children'),
    [
        Input('fig_by_fault', 'clickData'),
        Input('fig_by_trend', 'clickData')
    ])
def display_figure_trainmove(first_value, second_value):
    vobc_id = None
    fault_code = None
    if first_value != None:
        vobc_id = first_value['points'][0]['x']
        fault_code = first_value['points'][0]['curveNumber'] + 1 #click curveNumber is between 0 and 14
        if (fault_code > 15) :
            fault_code -= 15

    op_date = None
    if second_value != None:
        op_date = second_value['points'][0]['x']
    f = create_fig_by_trainmove(vobc_id, op_date, fault_code)
    return f#'hover : ' + json.dumps(first_value, indent=2) + '\nclick\n' + json.dumps(click_value, indent=2)


#####----------------------------------------------------
# @app.callback(
#     Output('clickoutput_bar', 'children'),
#     [
#         Input('fig_by_fault', 'clickData')
#     ])
# def clicked_bar_data(value):
#     return 'click: ' + json.dumps(value, indent=2)
'''
hover : {
  "points": [
    {
      "curveNumber": 17,
      "pointNumber": 31,
      "pointIndex": 31,
      "x": 228,
      "y": 1623,
      "label": 228,
      "value": 1623
    }
  ]
}
click
{
  "points": [
    {
      "curveNumber": 0,
      "pointNumber": 2,
      "pointIndex": 2,
      "x": "2015-03-13",
      "y": 190
    }
  ]
}'''
'''
@app.callback(
    Output('selectoutput_bar', 'children'),
    [
        Input('fig_by_fault', 'selectedData')
    ])
def select_bar_data(value):
    return 'select : ' +json.dumps(value, indent=2)

@app.callback(
    Output('relayoutoutput_bar', 'children'),
    [
        Input('fig_by_fault', 'relayoutData')
    ])
def relayout_bar_data(value):
    return 'relayout :' + json.dumps(value, indent=2)

@app.callback(
    Output('restyleoutput_bar', 'children'),
    [
        Input('fig_by_fault', 'restyleData')
    ])
def restyle_bar_data(value):
    return 'restyle:' + json.dumps(value, indent=2)



@app.callback(
    Output('clickoutput_area', 'children'),
    [
        Input('fig_by_trend', 'clickData')
    ])
def clicked_area_data(value):
    return 'click : ' + json.dumps(value, indent=2)


@app.callback(
    Output('selectoutput_area', 'children'),
    [
        Input('fig_by_trend', 'selectedData')
    ])
def select_area_data(value):
    return 'select :' + json.dumps(value, indent=2)


@app.callback(
    Output('relayoutoutput_area', 'children'),
    [
        Input('fig_by_trend', 'relayoutData')
    ])
def relayout_area_data(value):
    return 'relayout: ' + json.dumps(value, indent=2)


@app.callback(
    Output('restyleoutput_area', 'children'),
    [
        Input('fig_by_trend', 'restyleData')
    ])
def restyle_area_data(value):
    return 'restyle:' + json.dumps(value, indent=2)
'''