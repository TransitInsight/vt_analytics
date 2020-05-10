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
import plotly

import config as cfg


def test_ViewTrainmvoeClass():
    c = ViewTrainmoveClass(248, '2015-1-1 10:12', 3, timedelta(hours=1))
    c.create_fig()
    assert c.get_fig() != None

def test_ViewTrainmvoeClass_offset():
    c = ViewTrainmoveClass(248, '2015-1-1 10:12', 3, timedelta(hours=1.5))
    c.create_fig()
    assert c.get_fig() != None

def test_ViewTrainmvoeClass_add_velocity():
    c = ViewTrainmoveClass(248, '2015-1-1 10:12', 3, timedelta(hours=1.5))
    c.add_velocity_data()
    fig = c.get_fig()

    assert fig is not None
    assert len(fig.data) == 2
    assert (fig.data[0].name == 'Actual Velocity')
    assert isinstance(fig.data[1], plotly.graph_objs.Scatter)
    assert (fig.data[1].name == 'Max Velocity')

def test_ViewTrainmvoeClass_add_vobcfault():
    c = ViewTrainmoveClass(248, '2015-1-1 10:12', 3, timedelta(hours=1.5))
    c.add_vobc_fault()
    fig = c.get_fig()

    assert fig is not None
    assert len(fig.data) == 1
    assert (fig.data[0].name == 'Vobc Fault')
    assert isinstance(fig.data[0], plotly.graph_objs.Scatter)

def test_ViewTrainmvoeClass_add_door():
    c = ViewTrainmoveClass(248, '2015-1-1 10:12', 3, timedelta(hours=1.5))
    c.add_door_data()
    fig = c.get_fig()

    assert fig is not None
    assert len(fig.data) == 2
    assert (fig.data[0].name == 'Door Cmd')
    assert isinstance(fig.data[0], plotly.graph_objs.Scatter)


    assert (fig.data[1].name == 'Door Status')
    assert isinstance(fig.data[1], plotly.graph_objs.Scatter)
