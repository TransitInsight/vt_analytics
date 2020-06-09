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

import util as util
import config as cfg
import pytest

filter_start_date = '2014-01-01T00:00:00'
filter_end_date =  '2018-04-25T00:13:26.017995'

def test_trainmove():
    df = trainmoveDA.get_trainmove(135, '2015-01-03T10:51:30.160Z', '2015-01-13T11:51:30.160Z')

    assert len(df['activePassiveStatus'].unique() == 2)
    assert len(df['doorCmd'].unique() == 2)
    assert len(df['doorStatus'].unique() == 2)

    assert len(df['loggedAt']) > 100
    assert len(df['loggedAt']) > 101


def test_trainmove_door():
    df = trainmoveDA.get_trainmove(135, '2015-01-03T10:51:30.160Z', '2015-01-13T11:51:30.160Z')

    assert df.dtypes['doorCmd'] == 'int64'
    assert df.dtypes['doorStatus'] == 'int64'
    # assert df['doorCmd'].max() == 3
    # assert df['doorCmd'].min() == 2

    # assert df['doorStatus'].max() == 1
    # assert df['doorStatus'].min() == 0



    assert df['doorCmd'].max() == -5
    assert df['doorCmd'].min() == -15

    assert df['doorStatus'].max() == -25
    assert df['doorStatus'].min() == -35




def test_trainmove_exception():
    with pytest.raises(ValueError) as exception_info:
        trainmoveDA.get_trainmove(248, '2015-01-03T10:51:30.160Z', '2014-01-13T11:51:30.160Z')
    assert "start_date needs to be smaller than end_date" in str(exception_info.value)


def test_os_name():
    assert len(os.name) > 0
    

def test_get_unique_vobcid_list():
    x = trainmoveDA.get_unique_vobcid_list(filter_start_date,filter_end_date,153)
    assert x is not None


def test_split_df():
    df = pd.DataFrame({'Active': [0,0,0,0, 1, 1, 0, 0, 0]},
                    index=[0,1,2,3,4,5,6,7,8])

    df1 = df.assign(new=df.Active.diff().ne(0).cumsum())

    for g in df1.new.unique():
        g_df = df1[df1.new == g]
        print (g_df)

    assert len(df1.new.unique()) == 3
