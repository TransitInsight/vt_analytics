
from modules import module_switch_self_move as ms
import pandas as pd
from datetime import datetime as dt
from datetime import timedelta

import util as util
import config as cfg
import pytest



start_date = dt(2014, 1, 1)
end_date = dt(2020, 1, 1)
start_date, end_date  = util.date2str2(start_date, end_date )



def test_get_switch_amts():
    df = ms.get_switch_amts(101)
    assert df is not None
    assert isinstance(df, pd.DataFrame)
    assert df.empty == False

def test_get_switch_count():
    x = ms.get_switch_count()
    assert x is not None
    assert x is not 0

def test_gen_3d_df():
    df = ms.gen_3d_df()
    assert df is not None
    assert isinstance(df, pd.DataFrame)


def test_gen_graph_3d():
    x = ms.gen_graph_3d()
    assert x is not None
    assert x is not 0

