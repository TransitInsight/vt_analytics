import os,sys,inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir) 

from views import view_commLoss as vc
import pytest
import pandas as pd
import numpy
import plotly
from modules import module_vobcfault
import util as util
from datetime import datetime as dt

filter_start_date = dt(2015, 1, 1)
filter_end_date = dt(2016, 4, 1)

df = None
def test_generate_scatter_graph():
    with pytest.raises(Exception):
        vc.gen_scatter_graph(df, None, None, None, None, None)

def test_gen_bar_exceptions():
    with pytest.raises(Exception):
        assert vc.gen_bar_data(df)

def test_update_Scatter():
    x = vc._update_Scatter(filter_start_date, filter_end_date, -1, -1)
    assert x is not None
    a = vc._update_Scatter(None, None, -1, -1)
    b = vc._update_Scatter(filter_end_date, filter_start_date, -1, -1)
    assert a and b is not None