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


start_date = dt(2014, 1, 1)
end_date = dt(2020, 1, 1)
start_date, end_date  = util.date2str2(start_date, end_date )


def test_switchid_boxplot():
    if util.is_in_memory():
        return
    x = vs._switchid_boxplot(start_date,end_date, '100%')
    assert x is not None

click_data = {'points':[{'curveNumber': 0, 'marker.color': 27, 'marker.size': 1310.6796116504854, 'pointIndex': 69, 'pointNumber': 69, 'text': 27, 'x': 101, 'y': 158}]}
def test_switchid_boxplot_dates():
    if util.is_in_memory():
        return
    x = vs._switchid_boxplot_dates(start_date,end_date, '100%', click_data)
    assert x is not None

def test_datecheck():
    start_date = dt(2014, 1, 1)
    end_date = dt(2020, 1, 1)
    start_date, end_date  = util.date2str2(start_date, end_date )
    start_date,end_date = vs.datecheck(start_date, end_date)
    start_date1,end_date1 = vs.datecheck(end_date,start_date)
    assert start_date == start_date1
    assert end_date == end_date1


