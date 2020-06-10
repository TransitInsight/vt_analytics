## to make sure pytest on Azure Pipeline can find the module package in the root folder. 
import os,sys,inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir) 


from modules import module_vobcfault as vobcDA
from modules import module_trainmove as trainmoveDA
import pandas as pd
from datetime import datetime
from datetime import timedelta
import requests
import json
import pprint
import pytest

import util as util
import config as cfg
'2020-04-25T00:13:26.017995'
'2015-01-01T00:00:00'

'2015-01-16'

def test_get_count_by_fc():
    df_all = vobcDA.get_count_by(-1, '2015-01-01T00:00:00', '2020-04-25T00:13:26.017995')
    df_one = vobcDA.get_count_by(3, '2015-01-01T00:00:00', '2020-04-25T00:13:26.017995')
    assert  df_all['FaultCount'].count() > 0 
    assert  df_one['FaultCount'].count() > 0 
    assert  util.IsInMemoryTrue(df_all['FaultCount'].count() > df_one['FaultCount'].count())

def test_get_count_by_fc_date():
    end  = datetime(2015,1,1)
    start = end - timedelta(days=100)
    df_all = vobcDA.get_count_by(-1, start, end)
    assert  df_all['FaultCount'].count() > 0 


def test_runquery():
    df = util.run_query("SELECT faultName, loggedAt, velocity from dlr_vobc_fault where loggedAt >= '2014-01-01T00:00:00' and loggedAt < '2015-04-25T00:13:26.017995' LIMIT 2000 ")
    assert  df['loggedAt'].count() > 100 

def test_get_count_by_daterange():
    df1 = vobcDA.get_count_by(-1, '2014-01-01T00:00:00', '2014-04-25T00:13:26.017995')
    df2 = vobcDA.get_count_by(-1, '2014-01-01T00:00:00', '2014-05-25T00:13:26.017995')
    assert  df1['FaultCount'].count() > 0 
    assert  df2['FaultCount'].count() > 0 
    assert  util.IsInMemoryTrue( df1['FaultCount'].count() < df2['FaultCount'].count() )

def test_get_count_exception():
    with pytest.raises(ValueError) as exception_info:
        vobcDA.get_count_by(-1, '2017-01-01T00:00:00', '2014-04-25T00:13:26.017995')

    assert "start_date needs to be smaller than end_date" in str(exception_info.value)

def test_get_count_by_fc_one():
    df = vobcDA.get_count_by(3, '2015-01-06', '2020-04-25T00:13:26.017995')
    assert  df['FaultCount'].count() > 0 

def test_get_fc():
    df = vobcDA.get_all_fault()
    assert len(df['faultName'].unique()) == 15
    assert len(df['faultCode'].unique()) == 15

def test_get_fc_list_vobcid():
    df = vobcDA.get_fault_list('2015-01-01T10:00','2015-01-01T20:00', 248)
    assert df is not None
    assert df['loggedAt'].count() > 0
    dfSet = df['faultCodeSet'].unique()
    assert len(dfSet) > 1

def test_get_fc_list_nullvobc_nullfc():
    df = vobcDA.get_fault_list('2015-01-01T10:00','2015-01-01T20:00')

    assert df['loggedAt'].count() > 0
    dfSet = df['faultCodeSet'].unique()
    assert len(dfSet) > 1


def test_get_fc_list_faultcode_nullvobc():
    df = vobcDA.get_fault_list('2015-01-01T10:00','2015-01-01T20:00', None, 3)

    assert df['loggedAt'].count() > 0
    dfSet = df['faultCodeSet'].unique()
    assert util.IsInMemoryTrue(len(dfSet) == 2)
    dfFC = df['faultCode'].unique()
    assert util.IsInMemoryTrue(len(dfFC) == 1)
    assert util.IsInMemoryTrue(dfFC[0] == 3)

    dfVobc = df['vobcid'].unique()
    assert len(dfVobc) > 1    

def test_get_fc_list_faultcode_vobc():
    df = vobcDA.get_fault_list('2015-01-01T10:00','2015-01-01T20:00', 248, 3)

    assert df['loggedAt'].count() > 0
    dfSet = df['faultCodeSet'].unique()
    assert util.IsInMemoryTrue(len(dfSet) == 2)
    dfFC = df['faultCode'].unique()
    assert util.IsInMemoryTrue(len(dfFC) == 1)
    assert util.IsInMemoryTrue(dfFC[0] == 3)

    dfVobc = df['vobcid'].unique()
    assert util.IsInMemoryTrue(len(dfVobc) == 1)
    assert util.IsInMemoryTrue(dfVobc[0] == 248)


def test_get_fc_trend():
    df = vobcDA.get_count_trend(-1, '2014-01-01T00:00:00', '2015-04-25T00:13:26.017995', -1)
    #y_max = df.groupby(['LoggedDate']).max().max() * 1.01
    assert df['LoggedDate'].count() > 100
    assert len(df['faultName'].unique()) == 15

    df1 = vobcDA.get_count_trend(3, '2014-01-01T00:00:00', '2015-04-25T00:13:26.017995', -1)
    assert util.IsInMemoryTrue(df['LoggedDate'].count() > df1['LoggedDate'].count())


def test_get_fc_trend1():
    df = vobcDA.get_count_trend(-1, '2014-01-01T00:00:00', '2015-04-25T00:13:26.017995', -1)
    assert df['LoggedDate'].count() > 100
    assert len(df['faultName'].unique()) == 15

    df1 = vobcDA.get_count_trend(-1, '2014-01-01T00:00:00', '2015-04-25T00:13:26.017995', 2)
    assert util.IsInMemoryTrue(df['LoggedDate'].count() > df1['LoggedDate'].count())


def test_get_fc_location():
    df = vobcDA.get_count_location(-1, '2014-01-01T00:00:00', '2015-04-25T00:13:26.017995', -1)
    assert df['LocationName'].count() > 100
    assert len(df['faultName'].unique()) == 15

    df1 = vobcDA.get_count_trend(-1, '2014-01-01T00:00:00', '2015-04-25T00:13:26.017995', 2)
    assert util.IsInMemoryTrue(df['LocationName'].count() > df1['LoggedDate'].count())

def test_color():
    c = cfg.vobc_fault_color_dict[1]
    assert c != None

    c = cfg.vobc_fault_color_dict[-1]
    assert c != None

def test_fcname():
    for key, value in cfg.vobc_fault_name_dict.items():
        print(key, ":", value)
    fn = vobcDA.create_dropdown_options()
    assert len(fn) == 16

    fn0 = vobcDA.get_fault_name(-1)
    assert fn0 == '00. All'

def test_sum_PD():
    df = vobcDA.get_count_by(-1, '2014-01-01T00:00:00', '2015-04-25T00:13:26.017995')
    pprint.pprint(df.groupby(['VOBCID']).sum().FaultCount.max())
    #y_max = df.groupby(['VOBCID'])['FaultCount'].sum().max()


def test_str2date1():
    dt = util.str2date1('2010-1-1')
    assert isinstance(dt, datetime)


    dt = util.str2date1('2015-04-25T00:13:26.017995')
    assert isinstance(dt, datetime)
    assert dt.year == 2015

def test_get_first_fault_time():
    dt = vobcDA.get_first_fault_time('2015-07-03', 3, 78)
    assert util.IsInMemoryTrue( dt.year == 2015 )

def test_simple():
    a = 2*2
    assert a == 4

def test_simple1():
    a = 2*2*2
    assert a == 8
