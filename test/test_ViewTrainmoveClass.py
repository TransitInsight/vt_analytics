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
import pytest


def test_ViewTrainmvoeClass():
    c = ViewTrainmoveClass(135, '2015-1-12 00:07', 0, timedelta(hours=0))
    c.create_fig()
    assert c.get_fig() != None

def test_ViewTrainmvoeClass_offset():
    c = ViewTrainmoveClass(135, '2015-1-12 00:07', 0, timedelta(hours=0))
    c.create_fig()
    assert c.get_fig() != None

def test_ViewTrainmvoeClass_add_velocity():
    c = ViewTrainmoveClass(135, '2015-1-12 00:07', 0, timedelta(hours=0))
    c.add_velocity_data(0)
    fig = c.get_fig()

    assert fig is not None
    assert len(fig.data) == 2
    assert (fig.data[0].name == 'Actual Velocity')
    assert isinstance(fig.data[1], plotly.graph_objs.Scatter)
    assert (fig.data[1].name == 'Max Velocity')

def test_ViewTrainmvoeClass_add_vobcfault():
    c = ViewTrainmoveClass(135, '2015-1-12 00:07', 0, timedelta(hours=0))
    c.add_vobc_fault(0)
    fig = c.get_fig()

    assert fig is not None
    assert len(fig.data) == 0
    


def test_ViewTrainmvoeClass_add_door():
    c = ViewTrainmoveClass(135, '2015-1-12 00:07', 0, timedelta(hours=0))
    c.add_door_data(0)
    fig = c.get_fig()

    assert fig is not None
    assert len(fig.data) == 2
    assert (fig.data[0].name == 'Door Cmd')
    assert isinstance(fig.data[0], plotly.graph_objs.Scatter)


    assert (fig.data[1].name == 'Door Status')
    assert isinstance(fig.data[1], plotly.graph_objs.Scatter)



def test_ViewTrainmvoeClass_door_cmd_status():
    c = ViewTrainmoveClass(135, '2015-1-12 00:07', 0, timedelta(hours=0))
    df = c.trainmove_df['Door Status Tips'].unique()
    assert len(df) == 2
    assert df[0] in ['Door Status = Closed', 'Door Status = Open']
    assert df[1] in ['Door Status = Closed', 'Door Status = Open']

    df = c.trainmove_df['Door Cmd Tips'].unique()
    assert len(df) == 2
    assert df[0] in ['Door Cmd = Closed', 'Door Cmd = Open']
    assert df[1] in ['Door Cmd = Closed', 'Door Cmd = Open']

def test_ViewTrainmvoeClass_no_data():
    c = ViewTrainmoveClass(135, '2015-1-12 00:07', 0, timedelta(hours=0))

    c.start = datetime(2020, 1,1, 1,0,0)
    c.end = datetime(2020, 1,1, 2,0,0)
    c.update_figure_layout()
    fig = c.get_fig()

    assert fig is not None
    assert fig.layout.xaxis.range[0] == c.start
    assert fig.layout.xaxis.range[1] == c.end 


def test_ViewTrainmvoeClass_private_exception():
    c = ViewTrainmoveClass(135, '2015-1-12 00:07', 0, timedelta(hours=0))
    with pytest.raises(AttributeError) as exception_info:
        c.__read_base_data()
    
    assert 'has no attribute' in str(exception_info.value)
