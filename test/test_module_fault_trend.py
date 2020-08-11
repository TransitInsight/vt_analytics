from modules import module_fault_trend as mft
import pandas as pd
from datetime import datetime as dt
from datetime import timedelta
import requests
import json
import pprint

import util as util
import config as cfg
import pytest

start_date = '2015-01-01'
end_date = '2015-06-06'
#start_date, end_date  = util.date2str2(start_date, end_date )

def test_get_fault_count_per_month():
    df = mft.get_fault_count_per_month()
    assert df is not None
    assert isinstance(df, pd.DataFrame)
    assert df.empty == False

def test_get_distance_per_month():
    df = mft.get_distance_per_month()
    assert df is not None
    assert isinstance(df, pd.DataFrame)
    assert df.empty == False

def test_get_operating_hours_by_month():
    df = mft.get_operating_hours_by_month()
    assert df is not None
    assert isinstance(df, pd.DataFrame)
    assert df.empty == False

# def test_gen_faultcount_distance_ophour_list():
#     f = mft.gen_faultcount_distance_ophour_list(start_date, end_date)
#     assert f is not None    

def test_gen_faultcount_per_month():
    f = mft.gen_faultcount_per_month(start_date, end_date)
    assert f is not None    

def test_get_faults_by_type():
    df = mft.get_faults_by_type(start_date, end_date)
    assert df is not None
    assert isinstance(df, pd.DataFrame)
    assert df.empty == False

def test_gen_past_months_fault_by_type():
    f = mft.gen_past_months_fault_by_type(end_date, 6)
    assert f is not None    

# def gen_past_6_months_fault_by_type():
#     f = mft.gen_past_6_months_fault_by_type(end_date)
#     assert f is not None    

def test_get_fault_per_vobc():
    df = mft.get_fault_per_vobc(start_date, end_date)
    assert df is not None
    assert isinstance(df, pd.DataFrame)
    assert df.empty == False

def test_get_op_hour_per_vobc():
    df = mft.get_op_hour_per_vobc(start_date, end_date)
    assert df is not None
    assert isinstance(df, pd.DataFrame)
    assert df.empty == False

def test_gen_top_vobc_fault_past_months():
    fig = mft.gen_top_vobc_fault_past_months(end_date, 6)
    assert fig is not None

def test_get_fault_types_per_day():
    df = mft.get_fault_types_per_day(start_date, end_date)
    assert df is not None
    assert isinstance(df, pd.DataFrame)
    assert df.empty == False

def test_get_fault_names():
    df = mft.get_fault_names(start_date, end_date)
    assert df is not None
    df = mft.get_fault_name(4)
    assert df is not None

def test_gen_fault_trend_bar():
    fig = mft.gen_fault_trend_bar(start_date, 1)
    assert fig is not None

def get_vobc_fault_list():
    df = mft.get_vobc_fault_list(start_date, end_date)
    assert df is not None
   
def test_gen_vobc_fault_list():
    fig = mft.gen_vobc_fault_list(start_date)
    assert fig is not None