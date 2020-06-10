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
    assert util.IsInMemoryTrue(len(x.index) == 300)
    assert len(x.index) >= 100 


def test_get_faultcount_by_vobcid_loc_date():
    x = module_commLoss.get_commLoss_by_vobcid_loc_date(filter_start_date, filter_end_date, 240, None)
    assert len(x.index) >= 10