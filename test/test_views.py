## to make sure pytest on Azure Pipeline can find the module package in the root folder. 
import os,sys,inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir) 

from views import view_vobcfault as vobcView
from views.ViewTrainmoveClass import ViewTrainmoveClass
import pandas as pd
from datetime import datetime
from datetime import timedelta
import requests
import json
import pprint
import dash_core_components as dcc
import dash_bootstrap_components as dbc

import config as cfg

def test_create_fig_by_trend():
    ret = vobcView.create_fig_by_trend(-1, '2014-01-01T00:00:00', '2020-04-25T00:13:26.017995', -1)
    assert ret != None
    assert ret._data_objs != None
    assert len(ret._data_objs) == 30# two sub plots, and each contain 15 catagories

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


def test_create_fig_by_trainmove_Vobc_None():
    ret = vobcView.create_fig_by_trainmove(None, '2015-1-1 10:12', 3)
    assert ret != None

def test_create_fig_by_trainmove_Date_None():
    ret = vobcView.create_fig_by_trainmove(248, None, 3)
    assert ret != None

def test_trainmove_view_class():
    c = ViewTrainmoveClass(248, '2015-1-1 10:12', 3)
    c.create_fig()
    assert c.get_fig() != None


def test_trainmove_offset_callback():

    data = vobcView.update_offset( 1, 2, 0, 0, None)
    assert data['offset'] == -4

def test_traimove_fig_callback_none():
    ret = vobcView.display_figure_trainmove(None, None, None)
    assert ret is not None

def test_traimove_fig_callback():

    points1 = [{'curveNumber': 12, 'label': 13, 'pointIndex': 3, 'pointNumber': 3, 'value': 13, 'x': 13, 'y': 13}]
    first_value = {'points':points1}

    points2 = [{'curveNumber': 14, 'pointIndex': None, 'pointNumber': None, 'x': '2019-11-28', 'y': 0}]
    second_value = {'points':points2}

    timewindow_value = {'offset':0}

    ret = vobcView.display_figure_trainmove(first_value, second_value, timewindow_value)
    assert ret is not None


def test_displayarea_callback():
    a_selected_value = {'curveNumber': 12, 'label': 13, 'pointIndex': 3, 'pointNumber': 3, 'value': 13, 'x': 13, 'y': 13}
    list1 = [a_selected_value]
    click_value = {'points': list1}
    ret = vobcView.display_figure_area(3, '2015-01-01T00:00:00', '2015-04-01T00:00:00', click_value)
    assert ret is not None