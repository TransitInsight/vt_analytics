from views import view_fault_trend as vft
import pandas as pd
from datetime import datetime as dt
from datetime import timedelta
import requests
import json
import pprint

import util as util
import config as cfg
import pytest

start_date = dt(2014, 1, 1)
end_date = dt(2020, 1, 1)
start_date, end_date  = util.date2str2(start_date, end_date )



def test_datecheck():
    start_date = dt(2014, 1, 1)
    end_date = dt(2020, 1, 1)
    start_date, end_date  = util.date2str2(start_date, end_date )
    start_date,end_date = vft.datecheck(start_date, end_date)
    start_date1 , end_date1 = vft.datecheck(end_date,start_date)
    start_date2,end_date2 = vft.datecheck(None, None)
    assert start_date == start_date1
    assert end_date == end_date1
    assert start_date2 is not None
    assert end_date2 is not None

def test_fc_list():
    data = vft._fc_list(start_date,end_date)
    assert data is not None

def test_fault_trend():
    data = vft._fault_trend(start_date,end_date)
    assert data is not None

cd_1 = {'points':[{'curveNumber': 0, 'marker.color': 27, 'marker.size': 1310.6796116504854, 'pointIndex': 69, 'pointNumber': 69, 'text': 27, 'x': 101, 'y': 158}]}


def test_trainmove_offset_callback():

    items = [{'prop_id': 'vft_button_next_page.n_clicks'}]
    data = vft.update_offset( items, None)
    assert data['offset'] == 2

    items = [{'prop_id': 'vft_button_next.n_clicks'}]
    data = vft.update_offset( items, None)
    assert data['offset'] == 1

    items = [{'prop_id': 'vft_button_prev_page.n_clicks'}]
    data = vft.update_offset( items, None)
    assert data['offset'] == -2

    items = [{'prop_id': 'vft_button_prev.n_clicks'}]
    data = vft.update_offset( items, None)
    assert data['offset'] == -1