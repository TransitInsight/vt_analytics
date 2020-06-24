import os,sys,inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir) 


from modules import module_switch as ms
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


def test_get_switch_count():
    x = ms.get_switch_count(start_date, end_date)
    assert x is not None
    assert len(x) > 10

def test_get_switch_filter_val():
    x = ms.get_switch_filter_val(start_date, end_date, 101, 100)
    assert x is not None

def test_get_df():
    pool = mp.Pool(4)
    x= ms.get_df(pool, start_date, end_date,0 )
    assert x is not None
    assert len(x) > 10
    x= ms.update_val(pool, x, start_date, end_date)
    assert x is not None
    assert len(x) > 10
    pool.close()