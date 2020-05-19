## to make sure pytest on Azure Pipeline can find the module package in the root folder. 
import os,sys,inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir) 

from views import view_vobcfault as vobcView
import pandas as pd
from datetime import datetime
from datetime import timedelta
import requests
import json
import pprint
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import plotly
import dash_table

import config as cfg

def test_create_fig_by_trend():
    ret = vobcView.create_fig_by_trend(-1, '2014-01-01T00:00:00', '2020-04-25T00:13:26.017995', -1)
    assert ret != None
    assert ret._data_objs != None
    assert len(ret._data_objs) == 15

def test_create_fig_by_vobc():
    ret = vobcView.create_fig_by_vobc(-1, '2014-01-01T00:00:00', '2020-04-25T00:13:26.017995')
    assert ret != None
    assert ret._data_objs != None
    assert len(ret._data_objs) >= 15# two sub plots, and each contain 15 catagories

def test_create_layout():
    ret = vobcView.create_layout()
    assert ret != None
    assert ret.children != None
    assert ret.children[0] != None
    assert isinstance(ret.children[1], dbc.Row)

def test_create_fig_by_trainmove():
    ret = vobcView.create_fig_by_trainmove(248, '2015-1-1 10:12', 3)
    assert ret != None
    assert len(ret.data) == 6
    assert isinstance(ret.data[0], plotly.graph_objs.Scatter)
    assert (ret.data[0].name == 'Actual Velocity')
    assert isinstance(ret.data[1], plotly.graph_objs.Scatter)
    assert (ret.data[1].name == 'Max Velocity')
    assert isinstance(ret.data[2], plotly.graph_objs.Scatter)
    assert (ret.data[2].name == 'Vobc Fault')

    assert isinstance(ret.data[3], plotly.graph_objs.Scatter)
    assert (ret.data[3].name == 'Vobc Fault Rectified')



    assert isinstance(ret.data[4], plotly.graph_objs.Scatter)
    assert (ret.data[4].name == 'Door Cmd')
    assert isinstance(ret.data[5], plotly.graph_objs.Scatter)
    assert (ret.data[5].name == 'Door Status')



def test_create_fig_by_trainmove_Vobc_None():
    ret = vobcView.create_fig_by_trainmove(None, '2015-1-1 10:12', 3)
    assert ret != None

def test_create_fig_by_trainmove_Date_None():
    ret = vobcView.create_fig_by_trainmove(248, None, 3)
    assert ret != None

def test_trainmove_offset_callback():

    # if any ('button_prev_page.n_clicks' == item['prop_id'] for item in triggeredItems):
    #     offset = -2
    # elif any ('button_next_page.n_clicks' == item['prop_id'] for item in triggeredItems):
    #     offset = 2
    # elif any ('button_prev.n_clicks' == item['prop_id'] for item in triggeredItems):
    #     offset = -1
    # elif any ('button_next.n_clicks' == item['prop_id'] for item in triggeredItems):
    #     offset = 1

    items = [{'prop_id': 'button_next_page.n_clicks'}]
    data = vobcView.update_offset( items, None)
    assert data['offset'] == 2

    items = [{'prop_id': 'button_next.n_clicks'}]
    data = vobcView.update_offset( items, None)
    assert data['offset'] == 1

    items = [{'prop_id': 'button_prev_page.n_clicks'}]
    data = vobcView.update_offset( items, None)
    assert data['offset'] == -2

    items = [{'prop_id': 'button_prev.n_clicks'}]
    data = vobcView.update_offset( items, None)
    assert data['offset'] == -1


def test_traimove_fig_callback_none():
    ret = vobcView.display_figure_trainmove(None, None, None, None)
    assert ret is not None

def test_traimove_fig_callback():

    points1 = [{'curveNumber': 12, 'label': 13, 'pointIndex': 3, 'pointNumber': 3, 'value': 13, 'x': 13, 'y': 13}]
    first_value = {'points':points1}

    points2 = [{'curveNumber': 14, 'pointIndex': None, 'pointNumber': None, 'x': '2019-11-28', 'y': 0}]
    second_value = {'points':points2}

    timewindow_value = {'offset':0}

    ret = vobcView.display_figure_trainmove(first_value, second_value, None, timewindow_value)
    assert ret is not None


def test_displayarea_callback():
    a_selected_value = {'curveNumber': 12, 'label': 13, 'pointIndex': 3, 'pointNumber': 3, 'value': 13, 'x': 13, 'y': 13}
    list1 = [a_selected_value]
    click_value = {'points': list1}
    ret = vobcView.display_fault_trend(3, '2015-01-01T00:00:00', '2015-04-01T00:00:00', click_value)
    assert ret is not None

def test_displayarea_callback_none():
    ret = vobcView.display_fault_trend(3, '2015-01-01T00:00:00', '2015-04-01T00:00:00', None)
    assert ret is not None    


def test_display_figure_fault_list_callback():
    a_selected_value = {'curveNumber': 12, 'label': 13, 'pointIndex': 3, 'pointNumber': 3, 'value': 13, 'x': 280, 'y': 13}#x is VobcID
    list1 = [a_selected_value]
    click_value = {'points': list1}

    points2 = [{'curveNumber': 14, 'pointIndex': None, 'pointNumber': None, 'x': '2015-1-28', 'y': 0}]
    second_value = {'points':points2}

    ret = vobcView.display_figure_fault_list(3, '2015-01-01T00:00:00', '2015-04-01T00:00:00', click_value, second_value)
    assert ret is not None
    assert isinstance(ret, list)
    assert len(ret) >= 1
