import os,sys,inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir) 

from views import view_commLoss as vc
import pytest
import pandas as pd
import numpy
import plotly
from modules import module_vobcfault
import util as util
from datetime import datetime as dt

filter_start_date = dt(2015, 1, 1)
filter_end_date = dt(2016, 4, 1)

df = None
def test_generate_scatter_graph():
    with pytest.raises(Exception):
        vc.gen_scatter_graph(df, None, None, None, None, None)

def test_gen_bar_exceptions():
    with pytest.raises(Exception):
        assert vc.gen_bar_data(df)

def test_update_Scatter():
    x = vc._update_Scatter(filter_start_date, filter_end_date, -1, -1)
    assert x is not None
    a = vc._update_Scatter(None, None, -1, -1)
    b = vc._update_Scatter(filter_end_date, filter_start_date, -1, -1)
    assert a and b is not None

click_data = {'points':[{'curveNumber': 0, 'marker.color': 27, 'marker.size': 1310.6796116504854, 'pointIndex': 69, 'pointNumber': 69, 'text': 27, 'x': 'CAW', 'y': 158}]}
def test__display_click_data():
    x = vc._display_click_data(click_data,filter_start_date, filter_end_date, -1, -1 )
    assert x is not None
    a = vc._display_click_data(click_data,None, None, -1, -1 )
    b = vc._display_click_data(click_data,filter_end_date, filter_start_date, -1 , -1)
    c = vc._display_click_data(None,filter_start_date, filter_end_date, -1 , -1)
    assert a and b and c is not None

def test_display_figure_fault_list_callback():
    a_selected_value = {'curveNumber': 12, 'label': 13, 'pointIndex': 3, 'pointNumber': 3, 'value': 13, 'y': 280, 'x': None}#y is VobcID
    list1 = [a_selected_value]
    click_value = {'points': list1}

    points2 = [{'curveNumber': 14, 'pointIndex': None, 'pointNumber': None, 'x':  '2015-01-01T00:00:00', 'y': 0}]
    second_value = {'points':points2}

    ret = vc.display_figure_fault_list( click_value, second_value, -1, -1)
    assert ret is not None
    assert isinstance(ret, list)
    assert len(ret) >= 1


def test_create_fig_by_trainmove():
    ret = vc.create_fig_by_trainmove(153, '2015-1-1 10:12')
    assert ret != None
    assert util.IsInMemoryTrue(len(ret.data) >= 18)
    assert isinstance(ret.data[0], plotly.graph_objs.Scatter)
    assert (ret.data[0].name == 'Actual Velocity')
    assert isinstance(ret.data[1], plotly.graph_objs.Scatter)
    assert (ret.data[1].name == 'Max Velocity')
    assert isinstance(ret.data[2], plotly.graph_objs.Scatter)
    assert util.IsInMemoryTrue(ret.data[2].name == 'Door Cmd')

    assert util.IsInMemoryTrue(isinstance(ret.data[3], plotly.graph_objs.Scatter))
    assert util.IsInMemoryTrue((ret.data[3].name == 'Door Status'))

def test_trainmove_offset_callback():

    items = [{'prop_id': 'cL_button_next_page.n_clicks'}]
    data = vc.update_offset( items, None)
    assert data['offset'] == 2

    items = [{'prop_id': 'cL_button_next.n_clicks'}]
    data = vc.update_offset( items, None)
    assert data['offset'] == 1

    items = [{'prop_id': 'cL_button_prev_page.n_clicks'}]
    data = vc.update_offset( items, None)
    assert data['offset'] == -2

    items = [{'prop_id': 'cL_button_prev.n_clicks'}]
    data = vc.update_offset( items, None)
    assert data['offset'] == -1

def test_traimove_fig_callback_none():
    ret = vc.display_figure_trainmove(None, None,  None, None)
    assert ret is not None

def test_traimove_fig_callback():

    points2 = [{'curveNumber': 14, 'pointIndex': None, 'pointNumber': None, 'x': '2019-11-28', 'y': 0}]
    second_value = {'points':points2}
    
    timewindow_value = {'offset':0}

    ret = vc.display_figure_trainmove( second_value, None, None, timewindow_value)
    assert ret is not None
    ret1 = vc.display_figure_trainmove( second_value, None, None,  timewindow_value)
    assert ret1 is not None