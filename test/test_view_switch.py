from views import view_switch as vs
import pandas as pd
from datetime import datetime as dt
from datetime import timedelta
import requests
import json
import pprint

import util as util
import config as cfg
import pytest
import multiprocessing as mp
from pytest_mock import mocker
import sample_data_module_switch as s_ms

start_date = dt(2014, 1, 1)
end_date = dt(2020, 1, 1)
start_date, end_date  = util.date2str2(start_date, end_date )


def test_switchid_boxplot(mocker):
    mocker.patch("modules.module_switch.query_interval_by_switch", return_value= s_ms.sample_result_1)
    x = vs._switchid_boxplot(start_date,end_date, '100%')
    assert x is not None

click_data = {'points':[{'curveNumber': 0, 'marker.color': 27, 'marker.size': 1310.6796116504854, 'pointIndex': 69, 'pointNumber': 69, 'text': 27, 'x': 101, 'y': 158}]}
click_data1 = {'points':[{'curveNumber': 0, 'marker.color': 27, 'marker.size': 1310.6796116504854, 'pointIndex': 69, 'pointNumber': 69, 'text': 27, 'x': start_date , 'y': 158}]}

def test_switchid_boxplot_dates(mocker):
    mocker.patch("modules.module_switch.query_interval_by_date", return_value= s_ms.sample_result_dates)
    x = vs._switchid_boxplot_dates(start_date,end_date, '100%', click_data)
    assert x is not None
    x = vs._switchid_boxplot_dates(start_date,end_date, '100%', None)
    assert x == {}

def test_datecheck():
    start_date = dt(2014, 1, 1)
    end_date = dt(2020, 1, 1)
    start_date, end_date  = util.date2str2(start_date, end_date )
    start_date,end_date = vs.datecheck(start_date, end_date)
    start_date1,end_date1 = vs.datecheck(end_date,start_date)
    start_date2,end_date2 = vs.datecheck(None, None)
    assert start_date == start_date1
    assert end_date == end_date1
    assert start_date2 is not None
    assert end_date2 is not None

def test_switchid_line_dates():
    x = vs._switchid_line_dates(click_data1,click_data)
    assert x is not None

def test_switchid_line_dates_2():
    x = vs._switchid_line_dates(None,None)
    assert x ==  {}

