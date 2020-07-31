from views import view_mileage as vm
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


click_data = {'points':[{'curveNumber': 0, 'marker.color': 27, 'marker.size': 1310.6796116504854, 'pointIndex': 69, 'pointNumber': 69, 'text': 27, 'x': start_date , 'y': 158}]}
def test_fleet_mileage():
    fig = vm._fleet_mileage(start_date,end_date)
    assert fig is not None

# def test_mileage_by_train():
#     fig = vm._mileage_by_train(click_data)
#     assert fig is not None

def test__train_mileage():
    fig = vm._train_mileage(None, None)
    assert fig==[]

def test_datecheck():
    start_date = dt(2014, 1, 1)
    end_date = dt(2020, 1, 1)
    start_date, end_date  = util.date2str2(start_date, end_date )
    start_date,end_date = vm.datecheck(start_date, end_date)
    start_date1,end_date1 = vm.datecheck(end_date,start_date)
    start_date2,end_date2 = vm.datecheck(None, None)
    assert start_date == start_date1
    assert end_date == end_date1
    assert start_date2 is not None
    assert end_date2 is not None
