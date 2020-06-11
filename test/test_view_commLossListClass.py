import os,sys,inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir) 


from views.view_commLossListClass import ViewCommLossListClass as vc
import pandas as pd
from datetime import datetime
from datetime import timedelta
import plotly
import dash_table

import config as cfg
import pytest


def test_ViewFaultListClass_data():
    c = vc('TestTableID', '2015-1-1 10:12', '2015-1-2 10:12', 248)

    assert c.df is not None
    df = c.df
    assert len(df.index) > 0

def test_ViewFaultListClass_fig():
    c = vc('TestTableID', '2015-1-1 10:12', '2015-1-2 10:12', 248)
    c.create_fig()
    assert c is not None

    fig = c.get_fig()
    assert fig is not None
    #assert len(fig.data) > 1
    assert isinstance(fig, dash_table.DataTable)

def test_ViewFaultListClass_vobc_none():
    c = vc('TestTableID', '2015-1-1 10:12', '2015-1-2 10:12', None)
    assert c is not None

    c.create_fig()
    fig = c.get_fig()
    assert fig is not None
    #assert len(fig.data) > 1
    assert isinstance(fig, dash_table.DataTable)