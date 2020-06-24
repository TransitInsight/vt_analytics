from views import view_switch as vs
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


start_date = dt(2014, 1, 1)
end_date = dt(2020, 1, 1)
start_date, end_date  = util.date2str2(start_date, end_date )


def test_switchid_boxplot():
    x = vs._switchid_boxplot(start_date,end_date, .01)
    assert x is not None


# def test_get_max():
#     x = ms.get_max(start_date,end_date, 101, 4)
#     assert x is not None

# def test_gen_graph():
#     x = ms.gen_graph(None, start_date,end_date, 0)
#     assert x is not None

# def test_gen_graph_1():
#     x = ms.gen_graph(None, start_date,end_date, 0.0001)
#     assert x is not None

# def test_get_switch_filter_val_2():
#     x = ms.get_switch_filter_val(start_date, end_date, 101, 0)
#     assert x is not None