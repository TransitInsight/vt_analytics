from views import view_switch_self_move as vs
import pandas as pd
from datetime import datetime as dt
from datetime import timedelta
import requests
import json
import pprint

import util as util
import config as cfg
import pytest
import mock
from pytest_mock import mocker
import sample_data_module_switch as s_ms

start_date = dt(2014, 1, 1)
end_date = dt(2020, 1, 1)
start_date, end_date  = util.date2str2(start_date, end_date )
click_data = {'points':[{'curveNumber': 0, 'marker.color': 27, 'marker.size': 1310.6796116504854, 'pointIndex': 69, 'pointNumber': 69, 'text': 27, 'x': start_date , 'y': 101}]}
def test_switchid_self_move_line_dates():
    x = vs._switchid_self_move_line_dates(click_data)
    assert x is not None

def test_switchid_self_move_bxplt(mocker):
    mocker.patch("modules.module_switch.query_interval_by_date", return_value= s_ms.sample_result_dates)
    x =vs._switchid_self_move_bxplt(click_data)
    assert x is not None