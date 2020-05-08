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

class ViewTrainmoveClass:

    def __init__(self, vobc_id, op_date, fault_code, offset):
        self.vobc_id = vobc_id
        self.op_date = op_date
        self.fault_code = fault_code
        self.fig = go.Figure()
        self.offset = offset or timedelta(hours=0)

    def read_base_data(self):
        self.op_date = util.str2date1(self.op_date)
        first_fault_time = vobcfault_m.get_first_fault_time(self.op_date, self.fault_code, self.vobc_id)

        if (first_fault_time != None):
            self.start = first_fault_time - timedelta(minutes=5) + self.offset
        else:
            self.start = self.op_date + timedelta(hours=6) + self.offset

        self.end = self.start + timedelta(hours=1)    

        self.trainmove_df = trainmove_m.get_trainmove(self.vobc_id, self.start, self.end)


    def create_fig(self):
        self.read_base_data()
        self.add_data()
        #self.add_button()
        self.update_figure_layout()

    def add_data(self):

        if (self.vobc_id is None or self.op_date is None or self.fault_code is None):
            return 

        if (self.trainmove_df is None or self.trainmove_df.empty):
            return 

        self.fig.add_trace(go.Scatter(x=self.trainmove_df['loggedAt'], y=self.trainmove_df['velocity'],
                name = "Actual Velocity",
                text='Actual Velocity = ' + self.trainmove_df['velocity'].astype(str),
                line_color="goldenrod", mode='lines+markers', 
                marker=dict(size=4, 
                            symbol='circle-dot',
                            color="goldenrod"
                            )
                )) 

        self.fig.add_trace(go.Scatter(x=self.trainmove_df['loggedAt'], y=self.trainmove_df['maximumVelocity'],
                name = "Max Velocity",
                text='Max Velocity = ' + self.trainmove_df['maximumVelocity'].astype(str),
                line_color="green"
                )) 

        df_fc = vobcfault_m.get_fault_list(self.start,self.end,self.vobc_id)
        if (df_fc.empty):
            return
        self.fig.add_trace(go.Scatter(x=df_fc['loggedAt'], y=df_fc['velocity'], 
                name="Vobc Fault",
                #hover_name = "faultCode",
                text='Fault = ' + df_fc['faultName'],
                mode='markers', marker=dict(size=15, 
                                            symbol='x',
                                            color=list(map(cfg.get_fault_color, df_fc['faultCode']))
                                            )
                ))

    def add_button(self):
        self.fig.update_layout(
            updatemenus=[
                dict(
                    type="buttons",
                    direction="right",
                    active=0,
                    x=0.57,
                    y=1.2,
                    buttons=list([
                        dict(label="<<",
                            method="restyle",
                            args=[{"timewindow": [-2]}]),
                        dict(label="<",
                            method="restyle",
                            args=[{"timewindow": [-1]}]),
                        dict(label=">",
                            method="restyle",
                            args=[{"timewindow": [1]}]),
                        dict(label=">>",
                            method="restyle",
                            args=[{"timewindow": [2]}]),
                    ]),
                )
            ])

    def update_figure_layout(self):
        title = "Velocity (VOBC={})".format(self.vobc_id)
        self.fig.update_yaxes(title_text=title, showspikes=True)
        self.fig.update_xaxes(showspikes=True)
        self.fig.update_layout(height=300, margin=dict(l=20, r=20, t=30, b=20))


    def get_fig(self):
        return self.fig