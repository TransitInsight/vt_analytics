from views import view_scatter as vv

import pytest
import pandas as pd
import numpy
import plotly
from modules import module_vobcfault
import util as util
from datetime import datetime as dt

df = pd.read_csv('fault_code_test_data.csv', index_col= "LoggedAt")
df.index = pd.to_datetime(df.index)
df2 = None
df3 = df[df["FaultName"] == 0]

def sort_VOBCID_FaultCount(df, rtn_amt):
    df = df.groupby(["VOBCID", "LocationName"]).size()
    df = df.to_frame(name = 'FaultCount').reset_index()
    df = df.nlargest(rtn_amt,"FaultCount") 
    return df

def sort_by_VOBCID_Location(df, vobcid, loc_name):
    df = df[df['LocationName'].str.contains(loc_name)]
    df = df[df['VOBCID'] == (vobcid)]
    df = df.groupby(df.index.date).count()
    df = df["Fault Code"]
    df = df.to_frame(name = 'FaultCount')
    return df   

def sort_Dates(df, start_date, end_date):
    if start_date is not None and end_date is not None:
        if start_date > end_date:
            raise Exception("invalid dates")
        mask = (df.index >= start_date) & (df.index <= end_date)
        df = df.loc[mask]
    return df

def test_generate_scatter_graph():
    with pytest.raises(Exception):
        vv.gen_scatter_graph(df, None, None, None, None, None)

def test_generate_scatter():
    x = sort_VOBCID_FaultCount(df, 3000)
    data = vv.gen_scatter_graph_data(x, "LocationName", "VOBCID", 5000)
    assert isinstance(data, plotly.graph_objs.Scatter)
    assert data is not None       

# def test_gen_bar():
#     dft = sort_by_VOBCID_Location(df, 240, 'GRE-DEB')
#     data =  vv.gen_bar_data(dft)
#     assert data is not None
#     assert isinstance(data, plotly.graph_objs.Bar)

def test_gen_bar_exceptions():
    with pytest.raises(Exception):
        assert vv.gen_bar_data(df)



dictionary = [
 {'label': '00. All', 'value': -1},
 {'label': '01. Passenger Alarm', 'value': 1},
 {'label': '02. FAR Level 2 Fault', 'value': 2},
 {'label': '03. FAR Level 3 Fault', 'value': 3},
 {'label': '04. Failed to Dock', 'value': 4},
 {'label': '05. Dynamic Brake Failure', 'value': 5},
 {'label': '06. Converter Failure', 'value': 6},
 {'label': '07. FAR Level 1 Fault', 'value': 7},
 {'label': '08. Train Overspeed', 'value': 8},
 {'label': '09. Target Point Overshoot', 'value': 9},
 {'label': '10. Rollback', 'value': 10},
 {'label': '11. V = 0 Failure', 'value': 11},
 {'label': '12. Obstruction in AUTO Mode', 'value': 12},
 {'label': '13. EB Test Failure', 'value': 13},
 {'label': '14. Power Deselect Failure', 'value': 14},
 {'label': '15. Loss of Door Closed Status', 'value': 15}]
def test_dict_gen_scatterplot1():
    x = module_vobcfault.create_dropdown_options()
    assert x == dictionary

def test_import():
    x = util.run_query("SELECT min(loggedAt), max(loggedAt)  from dlr_train_move ")
    assert x is not None

filter_start_date = dt(2015, 1, 1)
filter_end_date = dt(2016, 4, 1)



def test_update_Scatter():
    x = vv._update_Scatter(3,filter_start_date, filter_end_date, -1, -1)
    assert x is not None
    a = vv._update_Scatter(3,None, None, -1, -1)
    b = vv._update_Scatter(3, filter_end_date, filter_start_date, -1, -1)
    assert a and b is not None

def test_get_faultcount_by_vobcid_loc_1():
    x = module_vobcfault.get_faultcount_by_vobcid_loc(filter_start_date, filter_end_date, 3)
    assert util.IsInMemoryTrue(len(x.index) == 300 )
    assert len(x.index) >= 100 

def test_get_faultcount_by_vobcid_loc_2():
    x = module_vobcfault.get_faultcount_by_vobcid_loc(filter_start_date, filter_end_date, 3, 0, 0)
    assert util.IsInMemoryTrue(len(x.index) == 285 )
    assert len(x.index) >= 100 

def test_get_faultcount_by_vobcid_loc_3():
    x = module_vobcfault.get_faultcount_by_vobcid_loc(filter_start_date, filter_end_date, 3, 1, 1)
    assert util.IsInMemoryTrue(len(x.index) == 300 )
    assert len(x.index) >= 100 

def test_get_faultcount_by_vobcid_loc_date_1():
    x = module_vobcfault.get_faultcount_by_vobcid_loc_date(filter_start_date, filter_end_date, 240, 3, None)
    assert len(x.index) >= 10

def test_get_faultcount_by_vobcid_loc_date_2():
    x = module_vobcfault.get_faultcount_by_vobcid_loc_date(filter_start_date, filter_end_date, 240, 3, None, 1, 1)
    assert len(x.index) >= 10

def test_get_faultcount_by_vobcid_loc_date_3():
    x = module_vobcfault.get_faultcount_by_vobcid_loc_date(filter_start_date, filter_end_date, 240, 3, None, 0, 0)
    assert len(x.index) >= 5

click_data = {'points':[{'curveNumber': 0, 'marker.color': 27, 'marker.size': 1310.6796116504854, 'pointIndex': 69, 'pointNumber': 69, 'text': 27, 'x': 'CAW', 'y': 158}]}
def test__display_click_data():
    x = vv._display_click_data(click_data,filter_start_date, filter_end_date, 3, -1, -1 )
    assert x is not None
    a = vv._display_click_data(click_data,None, None, 3, -1, -1 )
    b = vv._display_click_data(click_data,filter_end_date, filter_start_date, 3, -1 , -1)
    c = vv._display_click_data(None,filter_start_date, filter_end_date,  None, -1 , -1)
    assert a and b and c is not None

def test_datecheck():
    start_date,end_date = vv.datecheck(filter_start_date, filter_end_date)
    start_date1,end_date1 = vv.datecheck(filter_end_date,filter_start_date)
    assert start_date == start_date1
    assert end_date == end_date1


def test_create_fig_by_trainmove():
    ret = vv.create_fig_by_trainmove(153, '2015-1-1 10:12', 3)
    assert ret != None
    assert util.IsInMemoryTrue(len(ret.data) >= 18)
    assert isinstance(ret.data[0], plotly.graph_objs.Scatter)
    assert (ret.data[0].name == 'Actual Velocity')
    assert isinstance(ret.data[1], plotly.graph_objs.Scatter)
    assert (ret.data[1].name == 'Max Velocity')
    assert isinstance(ret.data[2], plotly.graph_objs.Scatter)
    assert util.IsInMemoryTrue(ret.data[2].name == 'Door Cmd')

    assert util.IsInMemoryTrue(isinstance(ret.data[3], plotly.graph_objs.Scatter))
    assert util.IsInMemoryTrue((ret.data[3].name == 'Door Status'))



    assert isinstance(ret.data[4], plotly.graph_objs.Scatter)
    #assert (ret.data[4].name == 'Door Cmd')
    #assert isinstance(ret.data[5], plotly.graph_objs.Scatter)
    #assert (ret.data[5].name == 'Door Status')


def test_create_fig_by_trainmove_Vobc_None():
    ret = vv.create_fig_by_trainmove(None, '2015-1-1 10:12', 3)
    assert ret != None

def test_create_fig_by_trainmove_Date_None():
    ret = vv.create_fig_by_trainmove(248, None, 3)
    assert ret != None

def test_traimove_fig_callback_none():
    ret = vv.display_figure_trainmove(None, None, None, None, None)
    assert ret is not None

def test_traimove_fig_callback():

    points1 = [{'curveNumber': 12, 'label': 13, 'pointIndex': 3, 'pointNumber': 3, 'value': 13, 'x': 13, 'y': 13}]
    first_value = {'points':points1}

    points2 = [{'curveNumber': 14, 'pointIndex': None, 'pointNumber': None, 'x': '2019-11-28', 'y': 0}]
    second_value = {'points':points2}
    
    points3 = [{'curveNumber': 18, 'label': 13, 'pointIndex': 3, 'pointNumber': 3, 'value': 13, 'x': 13, 'y': 13}]
    third_value = {'points':points3}
    timewindow_value = {'offset':0}

    ret = vv.display_figure_trainmove(first_value, second_value, None, None, timewindow_value)
    assert ret is not None
    ret1 = vv.display_figure_trainmove(third_value, second_value, None, None, timewindow_value)
    assert ret1 is not None
    
def test_display_figure_fault_list_callback():
    a_selected_value = {'curveNumber': 12, 'label': 13, 'pointIndex': 3, 'pointNumber': 3, 'value': 13, 'y': 280, 'x': None}#y is VobcID
    list1 = [a_selected_value]
    click_value = {'points': list1}

    points2 = [{'curveNumber': 14, 'pointIndex': None, 'pointNumber': None, 'x': '2015-1-28', 'y': 0}]
    second_value = {'points':points2}

    ret = vv.display_figure_fault_list(3, click_value, second_value, -1, -1)
    assert ret is not None
    assert isinstance(ret, list)
    assert len(ret) >= 1

def test_trainmove_offset_callback():

    items = [{'prop_id': 'vs_button_next_page.n_clicks'}]
    data = vv.update_offset( items, None)
    assert data['offset'] == 2

    items = [{'prop_id': 'vs_button_next.n_clicks'}]
    data = vv.update_offset( items, None)
    assert data['offset'] == 1

    items = [{'prop_id': 'vs_button_prev_page.n_clicks'}]
    data = vv.update_offset( items, None)
    assert data['offset'] == -2

    items = [{'prop_id': 'vs_button_prev.n_clicks'}]
    data = vv.update_offset( items, None)
    assert data['offset'] == -1
