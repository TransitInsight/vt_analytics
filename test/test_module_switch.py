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


def test_get_switch_count():
    x = ms.get_switch_count(start_date, end_date)
    assert x is not None
    assert len(x) > 10

def test_get_switch_filter_val():
    x = ms.get_switch_filter_val(start_date, end_date, 101, 100)
    assert x is not None

def test_get_df():
    t1 = time.time()
    pool = mp.Pool(4)
    t2 = time.time()
    delta = t2 - t1
    print ("pool init time = {}".format(delta))

    #time.sleep(10)
    t2 = time.time()
    x= ms.get_df(pool, start_date, end_date, 0 )
    t3 = time.time()
    delta = t3 - t2
    print ("get_df time = {}".format(delta))

    assert x is not None
    assert len(x) > 10
    x= ms.update_val(pool, x, start_date, end_date)

    t4 = time.time()
    delta = t4 - t3
    print ("update_val time = {}".format(delta))

    assert x is not None
    assert len(x) > 10
    pool.close()

def test_get_d0():
    x = ms.get_d0(start_date,end_date, 101, 4)
    assert x is not None

def test_get_avg():
    x = ms.get_avg(start_date,end_date, 101, 4)
    assert x is not None

def test_get_min():
    x = ms.get_min(start_date,end_date, 101, 4)
    assert x is not None

def test_gen_graph():
    x = ms.gen_graph(None, start_date,end_date, 0)
    assert x is not None

def test_gen_graph_1():
    x = ms.gen_graph(None, start_date,end_date, 0.0001)
    assert x is not None

def test_get_switch_filter_val_2():
    x = ms.get_switch_filter_val(start_date, end_date, 101, 0)
    assert x is not None

def test_get_unlock_count():
    x = ms.get_unlock_count(start_date, end_date)
    assert x is not None
    assert x is not 0



def query_interval_by_switch(start_date, end_date):

    start_date,end_date = util.date2str2(start_date,end_date)

    query_body = {
        "size": 0,
        "query" :  {
            "bool" : {
            "must" : [
                {
                "bool" : {
                    "must" : [
                    {
                        "terms" : {
                        "intervalDesc.keyword" : [
                            "Moving Time to Right",
                            "Moving Time to Left"
                        ],
                        "boost" : 1.0
                        }
                    },
                    {
                        "range" : {
                        "interval" : {
                            "from" : 0,
                            "to" : 2000,
                            "include_lower" : True,
                            "include_upper" : False,
                            "boost" : 1.0
                        }
                        }
                    }
                    ],
                    "adjust_pure_negative" : True,
                    "boost" : 1.0
                }
                },
                {
                "range" : {
                    "loggedAt" : {
                    "from" : start_date,
                    "to" : end_date,
                    "include_lower" : False,
                    "include_upper" : False,
                    "boost" : 1.0
                    }
                }
                }
            ],
            "adjust_pure_negative" : True,
            "boost" : 1.0
            }
        },

        "aggs": {
            "switchId": {
            "terms": {
                "field": "switchId",
                "size": 1000
            },

            "aggs": {
                "box_interval":{ 
                "percentiles": {
                    "field":"interval",
                    "percents": [
                    1,
                    25,
                    50,
                    75,
                    99,
                    99.9,
                    100
                    ]
                } 
                }
            }
            }
        }
    }    

    result = util.run_query_es_native('dlr_switch_move',  query_body)
    return result


def query_interval_by_date(switch_id, start_date, end_date):

    start_date,end_date = util.date2str2(start_date,end_date)

    query_body = {
        "size": 0,
        "query" :  {
            "bool" : {
            "must" : [
                {
                "bool" : {
                    "must" : [
                    {
                        "terms" : {
                        "intervalDesc.keyword" : [
                            "Moving Time to Right",
                            "Moving Time to Left"
                        ],
                        "boost" : 1.0
                        }
                    },
                    {
                        "term" : {
                        "switchId" : {
                            "value" : switch_id,
                            "boost" : 1.0
                        }
                        }
                    }
                    ],
                    "adjust_pure_negative" : True,
                    "boost" : 1.0
                }
                },
                {
                "bool" : {
                    "must" : [
                    {
                        "range" : {
                        "interval" : {
                            "from" : 0,
                            "to" : None,
                            "include_lower" : True,
                            "include_upper" : False,
                            "boost" : 1.0
                        }
                        }
                    },
                    {
                        "range" : {
                        "loggedAt" : {
                            "from" : start_date,
                            "to" : end_date,
                            "include_lower" : False,
                            "include_upper" : False,
                            "boost" : 1.0
                        }
                        }
                    }
                    ],
                    "adjust_pure_negative" : True,
                    "boost" : 1.0
                }
                }
            ],
            "adjust_pure_negative" : True,
            "boost" : 1.0
            }
        },

        "aggs": {
            "opDate": {
            "terms": {
                "field": "loggedDate",
                "size": 1000
            },

            "aggs": {
                "box_interval":{ 
                "percentiles": {
                    "field":"interval",
                    "percents": [
                    1,
                    25,
                    50,
                    75,
                    99,
                    99.9,
                    100
                    ]
                } 
                }
            }
            }
        }
    }


    result = util.run_query_es_native('dlr_switch_move',  query_body)
    return result


def test_switch_interval_es_native_query():

    if util.is_in_memory():
        return
    result = query_interval_by_switch('2014-1-1','2015-1-1')

    switch_1pct = result['aggregations']['switchId']['buckets'][0]['box_interval']['values']['1.0']
    switch_999pct = result['aggregations']['switchId']['buckets'][0]['box_interval']['values']['99.9']
    switch_990pct = result['aggregations']['switchId']['buckets'][0]['box_interval']['values']['99.0']

    assert(switch_999pct > switch_990pct)
    assert(switch_990pct > switch_1pct)
    assert(switch_1pct > 0)

    result = query_interval_by_switch('2014-1-1','2014-2-1')
    switch_1pct_n = result['aggregations']['switchId']['buckets'][0]['box_interval']['values']['1.0']
    switch_999pct_n = result['aggregations']['switchId']['buckets'][0]['box_interval']['values']['99.9']
    switch_990pct_n = result['aggregations']['switchId']['buckets'][0]['box_interval']['values']['99.0']

    assert(switch_999pct_n > switch_990pct_n)
    assert(switch_990pct_n > switch_1pct_n)
    assert(switch_1pct_n > 0)

    # whole year's percenile should be creater than 1 month's percentile
    assert(switch_999pct_n < switch_999pct)
    assert(switch_990pct_n < switch_990pct)
    #assert(switch_1pct_n < switch_1pct)


def test_switch_interval_by_date_es_native_query():

    if util.is_in_memory():
        return
    result = query_interval_by_date(101, '2014-1-1','2015-1-1')

    switch_1pct = result['aggregations']['opDate']['buckets'][0]['box_interval']['values']['1.0']
    switch_999pct = result['aggregations']['opDate']['buckets'][0]['box_interval']['values']['99.9']
    switch_990pct = result['aggregations']['opDate']['buckets'][0]['box_interval']['values']['99.0']

    assert(switch_999pct > switch_990pct)
    assert(switch_990pct > switch_1pct)
    assert(switch_1pct > 0)

    result = query_interval_by_date(101, '2014-1-1','2014-2-1')
    switch_1pct_n = result['aggregations']['opDate']['buckets'][0]['box_interval']['values']['1.0']
    switch_999pct_n = result['aggregations']['opDate']['buckets'][0]['box_interval']['values']['99.9']
    switch_990pct_n = result['aggregations']['opDate']['buckets'][0]['box_interval']['values']['99.0']

    assert(switch_999pct_n > switch_990pct_n)
    assert(switch_990pct_n > switch_1pct_n)
    assert(switch_1pct_n > 0)

