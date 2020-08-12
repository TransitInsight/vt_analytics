from views import view_fault_trend as vft
import pandas as pd
from datetime import datetime as dt
from datetime import timedelta
import requests
import json
import pprint

import util as util
import config as cfg
import pytest

start_date = dt(2014, 1, 1)
end_date = dt(2020, 1, 1)
start_date, end_date  = util.date2str2(start_date, end_date )



def test_datecheck():
    start_date = dt(2014, 1, 1)
    end_date = dt(2020, 1, 1)
    start_date, end_date  = util.date2str2(start_date, end_date )
    start_date,end_date = vft.datecheck(start_date, end_date)
    start_date1 , end_date1 = vft.datecheck(end_date,start_date)
    start_date2,end_date2 = vft.datecheck(None, None)
    assert start_date == start_date1
    assert end_date == end_date1
    assert start_date2 is not None
    assert end_date2 is not None