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


def f(x):
    time.sleep(5)
    return x*x

def is_prime(num):
    if num > 1:
        for i in range(2,num):
            if (num % i) == 0:
                return False
        else:
            return True
    else:
        return False 

def sum_prime1(x):
    total = 0
    for i in range (2,x):
        if is_prime(i):
            total += i
    print ("sum prime {}  = {}".format(x, total))            
    return total

def sum_prime(x):
    # print('.', end=' ')
    # sys.stdout.flush()
    r = sum_prime1(x)
    #time.sleep(5)
    return r


def test_single_thread_longrun():
    t1 = time.time()
    sum_prime(60000)
    sum_prime(60000)
    sum_prime(60000)
    sum_prime(60000)
    sum_prime(60000)
    sum_prime(60000)
    sum_prime(60000)
    sum_prime(60000)
    sum_prime(60000)
    sum_prime(60000)
    sum_prime(60000)
    sum_prime(60000)
    t2 = time.time()

    delta = t2 - t1
    print ("single thread duration = {}".format(delta))

def test_multithread_map_longrun():
    t2 = time.time()

    list_augs = [60000, 60000, 60000, 60000, 60000, 60000, 60000, 60000, 60000, 60000, 60000, 60000]
    p = mp.Pool(12)
    t3 = time.time()

    delta = t3 - t2
    print ("pool 1 init = {}".format(delta))

    p.map(sum_prime, list_augs)

    t4 = time.time()
    delta = t4 - t3
    print ("map calculation = {}".format(delta))

def test_multithread_mapstar_longrun():
    t4 = time.time()
    p = mp.Pool(processes=12)
    list_augs = [60000, 60000, 60000, 60000, 60000, 60000, 60000, 60000, 60000, 60000, 60000, 60000]

    t5 = time.time()
    delta = t5 - t4
    print ("pool 2 init  = {}".format(delta))

    p.starmap(sum_prime, product(list_augs, repeat=1))

    t6 = time.time()
    delta = t6 - t5
    print ("starmap  = {}".format(delta))

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

