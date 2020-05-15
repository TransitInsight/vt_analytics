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


def door_status_tip(row):
    if (row['doorStatus'] == -25):
        return 'Door Status = Open'
    elif (row['doorStatus'] == -35):
        return 'Door Status = Closed'
    else:
        assert False, "door status {} is not valid".format(row['doorStatus'])


def door_cmd_tip(row):
    if (row['doorCmd'] == -5):
        return 'Door Cmd = Open'
    elif (row['doorCmd'] == -15):
        return 'Door Cmd = Closed'
    else:
        assert False, "door cmd {} is not valid".format(row['doorCmd'])

class ViewTrainmoveClass:

    def __init__(self, vobc_id, op_date, fault_code, offset):
        self.vobc_id = vobc_id
        self.op_date = op_date
        self.fault_code = fault_code
        self.fig = go.Figure()
        self.offset = offset or timedelta(hours=0)
        self.read_base_data()

    def read_base_data(self):
        self.op_date = util.str2date1(self.op_date)
        first_fault_time = vobcfault_m.get_first_fault_time(self.op_date, self.fault_code, self.vobc_id)

        if (first_fault_time != None):
            self.start = first_fault_time - timedelta(minutes=5) + self.offset
        else:
            self.start = self.op_date + timedelta(hours=6) + self.offset

        self.end = self.start + timedelta(hours=1)    

        self.trainmove_df = trainmove_m.get_trainmove(self.vobc_id, self.start, self.end)
        #self.trainmove_df['Actual Velocity Toop Tips'] = 'Actual Velocity = {}\nLoop = {}'.format(self.trainmove_df['velocity'].astype(str), self.trainmove_df['loopName'])
        if not self.trainmove_df is None and not self.trainmove_df.empty:
            self.trainmove_df['Actual Velocity Toop Tips'] = 'Actual Velocity = ' + self.trainmove_df['velocity'].astype(str) + ' km/h<br>Loop = ' + self.trainmove_df['loopName']
            self.trainmove_df['Door Status Tips'] = self.trainmove_df.apply(door_status_tip, axis = 1)
            self.trainmove_df['Door Cmd Tips'] = self.trainmove_df.apply(door_cmd_tip, axis = 1)

    def create_fig(self):

        self.update_figure_layout()
        if (self.vobc_id is None or self.op_date is None or self.fault_code is None):
            return 

        if (self.trainmove_df is None or self.trainmove_df.empty):
            return 


        self.add_velocity_data()
        self.add_vobc_fault()
        self.add_door_data()
        #self.add_button()


    def add_velocity_data(self):

        self.fig.add_trace(go.Scatter(x=self.trainmove_df['loggedAt'], y=self.trainmove_df['velocity'],
                name = "Actual Velocity",
                text=self.trainmove_df['Actual Velocity Toop Tips'],
                line_color="goldenrod", mode='lines+markers', 
                line_width=1,
                marker=dict(size=3, 
                            symbol='circle-dot',
                            color="goldenrod"
                            )
                )) 

        self.fig.add_trace(go.Scatter(x=self.trainmove_df['loggedAt'], y=self.trainmove_df['maximumVelocity'],
                name = "Max Velocity",
                line_width=1,
                text='Max Velocity = ' + self.trainmove_df['maximumVelocity'].astype(str),
                line_color="green"
                )) 

    def add_door_data(self):

        self.fig.add_trace(go.Scatter(x=self.trainmove_df['loggedAt'], y=self.trainmove_df['doorCmd'],
                name = "Door Cmd",
                text=self.trainmove_df['Door Cmd Tips'],
                line_color="goldenrod", mode='lines+markers', 
                line_width=1,
                line_shape='hv',
                marker=dict(size=3, 
                            symbol='circle-dot',
                            color="goldenrod"
                            )
                )) 

        self.fig.add_trace(go.Scatter(x=self.trainmove_df['loggedAt'], y=self.trainmove_df['doorStatus'],
                name = "Door Status",
                line_width=1,
                text= self.trainmove_df['Door Status Tips'],
                line_color="green",
                line_shape='hv'
                )) 
    # add VOBC Fault, shows start time and rectified time
    # regardless actively selected the fault, we already include all fault types
    def add_vobc_fault(self):
        df_fc = vobcfault_m.get_fault_list(self.start,self.end,self.vobc_id)
        if (df_fc.empty):
            return

        df_fault = df_fc[df_fc['faultCodeSet'] == 1]    
        df_rectify = df_fc[df_fc['faultCodeSet'] == 0]    

        self.fig.add_trace(go.Scatter(x=df_fault['loggedAt'], y=df_fault['velocity'], 
                name="Vobc Fault",
                #hover_name = "faultCode",
                text='Fault = ' + df_fault['faultName'],
                mode='markers', marker=dict(size=7, 
                                            line=dict(width=1, color = list(map(cfg.get_fault_color, df_fault['faultCode']))),
                                            symbol='x',
                                            color=list(map(cfg.get_fault_color, df_fault['faultCode']))
                                            )
                ))

        self.fig.add_trace(go.Scatter(x=df_rectify['loggedAt'], y=df_rectify['velocity'], 
                name="Vobc Fault Rectified",
                #hover_name = "faultCode",
                text='Fault = ' + df_rectify['faultName'],
                mode='markers', marker=dict(size=7, 
                                            line=dict(width=1, color = 'darkgreen'),
                                            symbol='circle',
                                            color='darkgreen'
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
        ytitle = "Velocity (VOBC={})".format(self.vobc_id)

        xtitle = "date in ({} - {}), offset={}".format(self.start, self.end, self.offset)

        self.fig.update_yaxes(title_text=ytitle, showspikes=True)
        self.fig.update_xaxes(showspikes=True, range=[self.start, self.end], title_text=xtitle)
        self.fig.update_layout(height=300, margin=dict(l=20, r=20, t=30, b=20),legend_orientation="h")


    def get_fig(self):
        return self.fig