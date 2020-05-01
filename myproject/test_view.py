

#%%
import unittest
import myproject.views.vobcfault_v as vobcView
import pandas as pd
from datetime import datetime
from datetime import timedelta
import requests
import json
import pprint
import dash_core_components as dcc
import dash_bootstrap_components as dbc

import myproject.config as cfg

#%%
'2020-04-25T00:13:26.017995'
'2015-01-01T00:00:00'

'2015-01-16'

class TestVOBC_View(unittest.TestCase):

    def test_create_fig_by_trend(self):
        ret = vobcView.create_fig_by_trend(-1, '2014-01-01T00:00:00', '2020-04-25T00:13:26.017995', -1)
        self.assertTrue(ret != None)
        self.assertTrue(ret._data_objs != None)
        self.assertTrue(len(ret._data_objs) == 30)# two sub plots, and each contain 15 catagories

    def test_create_fig_by_vobc(self):
        ret = vobcView.create_fig_by_vobc(-1, '2014-01-01T00:00:00', '2020-04-25T00:13:26.017995')
        self.assertTrue(ret != None)
        self.assertTrue(ret._data_objs != None)
        self.assertTrue(len(ret._data_objs) == 30)# two sub plots, and each contain 15 catagories

    def test_create_layout(self):
        ret = vobcView.create_layout()
        self.assertTrue(ret != None)
        self.assertTrue(ret.children != None)
        self.assertTrue(ret.children[0] != None)
        self.assertTrue(isinstance(ret.children[0], dbc.Row))


if __name__ == '__main__':
    unittest.main()

# %%
