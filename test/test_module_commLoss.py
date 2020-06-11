import os,sys,inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir) 

from modules import module_commLoss
import pandas as pd
from datetime import datetime as dt
from datetime import timedelta
import requests
import json
import pprint
import pytest

import util as util
import config as cfg

filter_start_date = dt(2015, 1, 1)
filter_end_date = dt(2016, 4, 1)

def test_get_commLoss_by_vobcid_loc():
    x = module_commLoss.get_commLoss_by_vobcid_loc(filter_start_date, filter_end_date) 
    y = module_commLoss.get_commLoss_by_vobcid_loc(filter_start_date, filter_end_date,0,0)
    z = module_commLoss.get_commLoss_by_vobcid_loc(filter_start_date, filter_end_date,1,1)
    assert util.IsInMemoryTrue(len(x.index) == 300)
    assert len(x.index) >= 100 
    assert util.IsInMemoryTrue(len(y.index) == 300)
    assert len(y.index) >= 100 
    assert util.IsInMemoryTrue(len(z.index) == 300)
    assert len(z.index) >= 100 

def test_get_faultcount_by_vobcid_loc_date():
    x = module_commLoss.get_commLoss_by_vobcid_loc_date(filter_start_date, filter_end_date, 240, None)
    y = module_commLoss.get_commLoss_by_vobcid_loc_date(filter_start_date, filter_end_date, 240, None, 0, 0)
    z = module_commLoss.get_commLoss_by_vobcid_loc_date(filter_start_date, filter_end_date, 240, None, 1, 1)
    assert len(x.index) >= 10
    assert len(y.index) >= 10
    assert len(z.index) >= 10


def test_get_fc_list_faultcode_vobc_1():
    df = module_commLoss.get_commLoss_list('2015-01-01T10:00','2015-01-01T20:00', 248)
    assert df['loggedAt'].count() > 0
    dfVobc = df['vobcid'].unique()
    assert util.IsInMemoryTrue(len(dfVobc) == 1)
    assert util.IsInMemoryTrue(dfVobc[0] == 248)

def test_get_fc_list_faultcode_vobc_2():
    df = module_commLoss.get_commLoss_list('2015-01-01T10:00','2015-01-01T20:00', 248 , None, 1, 1, 1)
    assert df['loggedAt'].count() > 0
    dfVobc = df['vobcid'].unique()
    assert util.IsInMemoryTrue(len(dfVobc) == 1)
    assert util.IsInMemoryTrue(dfVobc[0] == 248)

def test_get_fc_list_faultcode_vobc_3():
    df = module_commLoss.get_commLoss_list('2015-01-01T10:00','2015-01-01T20:00', 248, None, 0, 0, 0)
    assert df.empty

    