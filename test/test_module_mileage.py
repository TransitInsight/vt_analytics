from modules import module_mileage as mm
import pandas as pd
from datetime import datetime as dt
from datetime import timedelta
import requests
import json
import pprint

import util as util
import config as cfg
import pytest

start_date = dt(2015, 1, 1)
end_date = dt(2015, 3, 1)
start_date, end_date  = util.date2str2(start_date, end_date )

def test_get_fleet_daily_mileage():
    df = mm.get_fleet_daily_mileage(start_date, end_date)
    assert df is not None
    assert isinstance(df, pd.DataFrame)
    assert df.empty == False

def test_get_mileage_by_train():
    df = mm.get_mileage_by_train(start_date, end_date)
    assert df is not None
    assert isinstance(df, pd.DataFrame)
    assert df.empty == False

def test_get_train_total_mileage():
    df = mm.get_train_total_mileage()
    assert df is not None
    assert isinstance(df, pd.DataFrame)
    assert df.empty == False
    

def test_get_train_mileage_by_30min():
    df = mm.get_train_mileage_by_30min(4, start_date, end_date)
    assert df is not None
    assert isinstance(df, pd.DataFrame)
    assert df.empty == False

def test_get_train_mileage_by_loop():
    df = mm.get_train_mileage_by_loop(4, start_date, end_date)
    assert df is not None
    assert isinstance(df, pd.DataFrame)
    assert df.empty == False

def test_gen_fleet_daily_mileage_graph():
    fig = mm.gen_fleet_daily_mileage_graph(start_date,end_date)
    assert fig is not None 

# def test_gen_mileage_by_train_table():
#     startdate = dt(2015, 2, 1)
#     fig = mm.gen_mileage_by_train_table(startdate)
#     assert fig is not None 

# def test_gen_train_mileage_table():
#     startdate = dt(2015, 2, 1)
#     fig = mm.gen_train_mileage_table(4, startdate)
#     assert fig is not None
