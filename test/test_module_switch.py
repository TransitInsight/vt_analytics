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
    pool = mp.Pool(12)
    t2 = time.time()
    delta = t2 - t1
    print ("pool init time = {}".format(delta))

    #time.sleep(10)
    t2 = time.time()
    x= ms.get_df(pool, start_date, end_date,0 )
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
