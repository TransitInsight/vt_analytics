# import myproject.views.vobcfault_v as vobcView
# import pandas as pd
# from datetime import datetime
# from datetime import timedelta
# import requests
# import json
# import pprint
# import dash_core_components as dcc
# import dash_bootstrap_components as dbc

# import myproject.config as cfg

# def test_create_fig_by_trend():
#     ret = vobcView.create_fig_by_trend(-1, '2014-01-01T00:00:00', '2020-04-25T00:13:26.017995', -1)
#     assert ret != None
#     assert ret._data_objs != None
#     assert len(ret._data_objs) == 30# two sub plots, and each contain 15 catagories

# def test_create_fig_by_vobc():
#     ret = vobcView.create_fig_by_vobc(-1, '2014-01-01T00:00:00', '2020-04-25T00:13:26.017995')
#     assert ret != None
#     assert ret._data_objs != None
#     assert len(ret._data_objs) >= 15# two sub plots, and each contain 15 catagories

# def test_create_layout():
#     ret = vobcView.create_layout()
#     assert ret != None
#     assert ret.children != None
#     assert ret.children[0] != None
#     assert isinstance(ret.children[0], dbc.Row)

# def test_create_fig_by_trainmove():
#     ret = vobcView.create_fig_by_trainmove(248, '2015-1-1 10:12', 3)
#     assert ret != None
