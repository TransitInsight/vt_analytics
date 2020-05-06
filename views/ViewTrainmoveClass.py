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

    def __init__(self, vobc_id, op_date, fault_code):
        self.vobc_id = vobcfault_m
        self.op_date = op_date
        self.fault_code = fault_code
        self.fig = go.Figure()

    def create_fig(self):
        if (self.vobc_id is None or self.op_date is None or self.fault_code is None):
            return 

        op_date = util.str2date1(self.op_date)
        first_fault_time = vobcfault_m.get_first_fault_time(self.op_date, self.fault_code, self.vobc_id)

        if (first_fault_time != None):
            start = first_fault_time - timedelta(minutes=5)
        else:
            start = op_date + timedelta(hours=6)
        end = start + timedelta(hours=1)    

        df = trainmove_m.get_trainmove(self.vobc_id, start, end)
        if (df.empty):
            return 

        self.fig.add_trace(go.Scatter(x=df['loggedAt'], y=df['velocity'],
                name = "Actual Velocity",
                text='Actual Velocity = ' + df['velocity'].astype(str),
                line_color="goldenrod"
                )) 

        self.fig.add_trace(go.Scatter(x=df['loggedAt'], y=df['maximumVelocity'],
                name = "Max Velocity",
                text='Max Velocity = ' + df['maximumVelocity'].astype(str),
                line_color="green"
                )) 
        title = "Velocity (VOBC={})".format(self.vobc_id)

        df_fc = vobcfault_m.get_fault_list(start,end,self.vobc_id)
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
        self.fig.update_yaxes(title_text=title, showspikes=True)
        self.fig.update_xaxes(showspikes=True)


    def get_fig(self):
        return self.fig