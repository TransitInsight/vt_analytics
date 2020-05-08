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

def test_trainmove():
    df = trainmoveDA.get_trainmove(248, '2015-01-03T10:51:30.160Z', '2015-01-13T11:51:30.160Z')

    assert len(df['activePassiveStatus'].unique() == 2)
    assert len(df['doorCmd'].unique() == 2)
    assert len(df['doorStatus'].unique() == 2)

    assert len(df['loggedAt']) > 100
    assert len(df['loggedAt']) > 101

