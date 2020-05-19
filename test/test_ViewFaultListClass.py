## to make sure pytest on Azure Pipeline can find the module package in the root folder. 
import os,sys,inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir) 

from views import view_vobcfault as vobcView
from views.ViewFaultListClass import ViewFaultListClass
import pandas as pd
from datetime import datetime
from datetime import timedelta
import plotly
import dash_table

import config as cfg
import pytest


def test_ViewFaultListClass_data():
    c = ViewFaultListClass('TestTableID', 3, '2015-1-1 10:12', '2015-1-2 10:12', 248)

    assert c.fc_df is not None
    df = c.fc_df
    assert len(df.index) > 0

def test_ViewFaultListClass_fig():
    c = ViewFaultListClass('TestTableID', 3, '2015-1-1 10:12', '2015-1-2 10:12', 248)
    c.create_fig()
    assert c is not None

    fig = c.get_fig()
    assert fig is not None
    assert len(fig.data) > 1
    assert isinstance(fig, dash_table.DataTable)

def test_ViewFaultListClass_vobc_none():
    c = ViewFaultListClass('TestTableID', 3, '2015-1-1 10:12', '2015-1-2 10:12', None)
    assert c is not None

    c.create_fig()
    fig = c.get_fig()
    assert fig is not None
    assert len(fig.data) > 1
    assert isinstance(fig, dash_table.DataTable)





