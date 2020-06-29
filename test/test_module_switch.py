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
from itertools import product
import time

 
start_date = dt(2014, 1, 1)
end_date = dt(2020, 1, 1)
start_date, end_date  = util.date2str2(start_date, end_date )



def test_gen_graph():
    x = ms.gen_graph(None, start_date,end_date, '100%')
    assert x is not None

def test_gen_graph_1():
    x = ms.gen_graph(None, start_date,end_date, '99.9%')
    assert x is not None



def test_get_unlock_count():
    x = ms.get_unlock_count(start_date, end_date)
    assert x is not None
    assert x is not 0


def test_switch_interval_es_native_query():

    if util.is_in_memory():
        return
    result = ms.query_interval_by_switch('2014-1-1','2015-1-1')

    switch_1pct = result['aggregations']['switchId']['buckets'][0]['box_interval']['values']['1.0']
    switch_999pct = result['aggregations']['switchId']['buckets'][0]['box_interval']['values']['99.9']
    switch_990pct = result['aggregations']['switchId']['buckets'][0]['box_interval']['values']['99.0']

    assert(switch_999pct > switch_990pct)
    assert(switch_990pct > switch_1pct)
    assert(switch_1pct > 0)

    result = ms.query_interval_by_switch('2014-1-1','2014-7-1')
    switch_1pct_n = result['aggregations']['switchId']['buckets'][0]['box_interval']['values']['1.0']
    switch_999pct_n = result['aggregations']['switchId']['buckets'][0]['box_interval']['values']['99.9']
    switch_990pct_n = result['aggregations']['switchId']['buckets'][0]['box_interval']['values']['99.0']

    assert(switch_999pct_n > switch_990pct_n)
    assert(switch_990pct_n > switch_1pct_n)
    assert(switch_1pct_n > 0)

    # whole year's percenile should be creater than 1 month's percentile
  #  assert(switch_999pct_n < switch_999pct)
   # assert(switch_990pct_n < switch_990pct)
    #assert(switch_1pct_n < switch_1pct)


def test_switch_interval_by_date_es_native_query():

    if util.is_in_memory():
        return
    result = ms.query_interval_by_date(101, '2014-1-1','2015-1-1')

    switch_1pct = result['aggregations']['opDate']['buckets'][0]['box_interval']['values']['1.0']
    # switch_999pct = result['aggregations']['opDate']['buckets'][0]['box_interval']['values']['99.9']
    #switch_990pct = result['aggregations']['opDate']['buckets'][0]['box_interval']['values']['99.0']

    #assert(switch_999pct > switch_990pct)
    #assert(switch_990pct > switch_1pct)
    assert(switch_1pct > 0)

    result = ms.query_interval_by_date(101, '2014-1-1','2014-7-1')
    switch_1pct_n = result['aggregations']['opDate']['buckets'][0]['box_interval']['values']['1.0']
    #switch_999pct_n = result['aggregations']['opDate']['buckets'][0]['box_interval']['values']['99.9']
    #switch_990pct_n = result['aggregations']['opDate']['buckets'][0]['box_interval']['values']['99.0']

    #assert(switch_999pct_n > switch_990pct_n)
    #assert(switch_990pct_n > switch_1pct_n)
    assert(switch_1pct_n > 0)

# def test_get_switch_count():
#     x = ms.get_switch_count(start_date, end_date)
#     assert x is not None
#     assert len(x) > 10

# def test_get_switch_filter_val():
#     x = ms.get_switch_filter_val(start_date, end_date, 101, 100)
#     assert x is not None

# def test_get_df():
#     t1 = time.time()
#     pool = mp.Pool(4)
#     t2 = time.time()
#     delta = t2 - t1
#     print ("pool init time = {}".format(delta))

#     #time.sleep(10)
#     t2 = time.time()
#     x= ms.get_df(pool, start_date, end_date, 0 )
#     t3 = time.time()
#     delta = t3 - t2
#     print ("get_df time = {}".format(delta))

#     assert x is not None
#     assert len(x) > 10
#     x= ms.update_val(pool, x, start_date, end_date)

#     t4 = time.time()
#     delta = t4 - t3
#     print ("update_val time = {}".format(delta))

#     assert x is not None
#     assert len(x) > 10
#     pool.close()

# def test_get_d0():
#     x = ms.get_d0(start_date,end_date, 101, 4)
#     assert x is not None

# def test_get_avg():
#     x = ms.get_avg(start_date,end_date, 101, 4)
#     assert x is not None

# def test_get_min():
#     x = ms.get_min(start_date,end_date, 101, 4)
#     assert x is not None

# def test_get_switch_filter_val_2():
#     x = ms.get_switch_filter_val(start_date, end_date, 101, 0)
#     assert x is not None