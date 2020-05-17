import os,sys,inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir) 


#%%
import json
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
from datetime import datetime
from datetime import timedelta

from app import app

from modules import module_vobcfault as vobcfault_m
from modules import module_trainmove as trainmove_m
import config as cfg
import util as util
import pandas as pd
import plotly.graph_objs as go
from plotly.subplots import make_subplots


class ViewFaultListClass:
    def __init__(self, fault_code, start_date, end_date, vobc_id):
        self.vobc_id = vobc_id
        self.start_date = start_date
        self.end_date = end_date
        self.fault_code = fault_code
        self.__fig = go.Figure()
        self.__read_base_data()

    def __read_base_data(self):
        self.fc_df = vobcfault_m.get_fault_list(self.start_date, self.end_date, self.vobc_id, self.fault_code)

    def create_fig(self):
        self.update_figure_layout()
        if (self.fc_df is None or self.fc_df.empty):
            return 
        self.add_vobc_fault_list()

    # add VOBC Fault, shows start time and rectified time
    # regardless actively selected the fault, we already include all fault types
    def add_vobc_fault_list(self):

        if (self.fc_df.empty):
            return

        df = self.fc_df
        self.__fig.add_trace(go.Table(
            header = dict(values = list(df.columns),
                          fill_color='paleturquoise',
                          align='left'),
            cells = dict(values=[df.loggedAt, df.faultName, df.velocity],
                         fill_color='lavender',
                         align='left')
            )
        )

    def update_figure_layout(self):
        ytitle = "Velocity (VOBC={})".format(self.vobc_id)
        self.__fig.update_yaxes(title_text=ytitle, showspikes=True)
        self.__fig.update_layout(height=300, margin=dict(l=20, r=20, t=30, b=20),legend_orientation="h")

    def get_fig(self):
        return self.__fig