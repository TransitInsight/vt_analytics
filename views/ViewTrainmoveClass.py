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

    def __init__(self,  parent_id, op_date, fault_code, offset):
        self.parent_id = parent_id
        self.op_date = op_date
        self.offset = offset or timedelta(hours=0)
        self.fault_code = fault_code
        self.get_unique_vobcid_list()
        x = len(self.vobc_id)
        if x > 0:
            assert x < 20
            self.fig = make_subplots(rows = x, cols=1, shared_xaxes=True,vertical_spacing=0.02)
        else:
            self.fig = make_subplots(rows = 1, cols=1, shared_xaxes=True,vertical_spacing=0.02)
        self.__read_base_data()

    def __read_base_data(self):

        self.trainmove_df = trainmove_m.get_trainmove(self.parent_id, self.start, self.end)
        #self.trainmove_df['Actual Velocity Toop Tips'] = 'Actual Velocity = {}\nLoop = {}'.format(self.trainmove_df['velocity'].astype(str), self.trainmove_df['loopName'])
        if self.trainmove_df is None or self.trainmove_df.empty:
            pass

        if not self.trainmove_df is None and not self.trainmove_df.empty:
            self.trainmove_df['Actual Velocity Toop Tips'] = 'Actual Velocity = ' + self.trainmove_df['velocity'].astype(str) + ' km/h<br>Loop = ' + self.trainmove_df['loopName']
            self.trainmove_df['Door Status Tips'] = self.trainmove_df.apply(door_status_tip, axis = 1)
            self.trainmove_df['Door Cmd Tips'] = self.trainmove_df.apply(door_cmd_tip, axis = 1)
        
        self.trainmove_df_list = []
        for i in range(len(self.vobc_id)):
            self.trainmove_df_list.append(self.trainmove_df[(self.trainmove_df['vobcid']==self.vobc_id[i])])
        
    
    def get_unique_vobcid_list(self):
        self.op_date = util.str2date1(self.op_date)
        self.start = self.op_date - timedelta(hours=0.25) + self.offset
        self.end = self.start + timedelta(hours=.5) 
        self.vobc_id = trainmove_m.get_unique_vobcid_list(self.start, self.end, self.parent_id)

    def create_fig(self):

        self.update_figure_layout()
        if (self.vobc_id is None or self.op_date is None or self.fault_code is None):
            return 

        if (self.trainmove_df is None or self.trainmove_df.empty):
            return 
        L = True
        for i in range(len(self.vobc_id)):            
            self.add_velocity_data(i,L)
            self.add_vobc_fault(i,L)
            self.add_door_data(i,L)
            ytitle = "VOBC={}".format(self.vobc_id[i])
            self.fig.update_yaxes(title_text=ytitle, row=i+1, col=1, showspikes=True)
            L = False


    def create_subplot_fig(self):
        self.update_figure_layout()

    def create_act_vel(self, df, color, i, L = False):
        self.fig.add_trace(go.Scatter(x=df["loggedAt"], y=df['velocity'],
                name = "Actual Velocity",
                #text=df['Actual Velocity Toop Tips'],
                line_color=color, mode='lines+markers', 
                line_width=1,
                connectgaps=False,
                showlegend=L,
                marker=dict(size=3, 
                            symbol='circle-dot',
                            color= color
                            )
                ),row=i+1, col=1) 

    def create_max_vel(self,df,color,i,L = False):
        self.fig.add_trace(go.Scatter(x=df["loggedAt"], y=df['maximumVelocity'],
                name = "Max Velocity",
                line_width=1,
                #text='Max Velocity = ' + df['maximumVelocity'].astype(str),
                line_color=color,
                connectgaps=False,
                showlegend=L
                ),row=i+1, col=1) 

   

    def add_velocity_data(self, i, L = False):
        df = self.trainmove_df_list[i].copy()
        df1 = df.assign(new=df["activePassiveStatus"].diff().ne(0).cumsum())
        dfList = [df1[df1.new == g] for g in df1.new.unique()]
        
        if dfList is None:
            return 
        
        for j in range(len(dfList)):
            if dfList[j] is not None or not dfList[j].empty:
                if dfList[j].iloc[0]["activePassiveStatus"] == True:
                    self.create_act_vel(dfList[j],"goldenrod",i,L)
                    self.create_max_vel(dfList[j],"green",i,L)
                else:
                    self.create_act_vel(dfList[j],"grey",i,L)
                    self.create_max_vel(dfList[j],"grey",i,L)
            L = False       

    def add_door_data(self, i, L = False):
        df = self.trainmove_df_list[i]
        self.fig.add_trace(go.Scatter(x=df['loggedAt'], y=df['doorCmd'],
                name = "Door Cmd",
                text=df['Door Cmd Tips'],
                line_color="goldenrod", mode='lines+markers', 
                line_width=1,
                line_shape='hv',
                showlegend=L, 
                marker=dict(size=3, 
                            symbol='circle-dot',
                            color="goldenrod"
                            )
                ),row=i+1, col=1) 

        self.fig.add_trace(go.Scatter(x=df['loggedAt'], y=df['doorStatus'],
                name = "Door Status",
                line_width=1,
                text= df['Door Status Tips'],
                line_color="green",
                line_shape='hv',
                showlegend=L
                ),row=i+1, col=1) 
    # add VOBC Fault, shows start time and rectified time
    # regardless actively selected the fault, we already include all fault types
    def add_vobc_fault(self, i, L = False):
        df_fc = vobcfault_m.get_fault_list(self.start,self.end,self.vobc_id[i])
        if (df_fc is None or df_fc.empty):
            return

        df_fault = df_fc[df_fc['faultCodeSet'] == 1]    
        df_rectify = df_fc[df_fc['faultCodeSet'] == 0]    

        self.fig.add_trace(go.Scatter(x=df_fault['loggedAt'], y=df_fault['velocity'], 
                name="Vobc Fault",
                #hover_name = "faultCode",
                text='Fault = ' + df_fault['faultName'],
                showlegend=L, 
                mode='markers', marker=dict(size=7, 
                                            line=dict(width=1, color = list(map(cfg.get_fault_color, df_fault['faultCode']))),
                                            symbol='x',
                                            color=list(map(cfg.get_fault_color, df_fault['faultCode']))
                                            )
                ),row=i+1, col=1)

        self.fig.add_trace(go.Scatter(x=df_rectify['loggedAt'], y=df_rectify['velocity'], 
                name="Vobc Fault Rectified",
                #hover_name = "faultCode",
                text='Fault = ' + df_rectify['faultName'],
                showlegend=L, 
                mode='markers', marker=dict(size=7, 
                                            line=dict(width=1, color = 'darkgreen'),
                                            symbol='circle',
                                            color='darkgreen'
                                            )
                ),row=i+1, col=1)

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
        h = 250 * len(self.vobc_id) 
        if h is 0:
            h = 250
        self.fig.update_xaxes(showspikes=True, range=[self.start, self.end])
        self.fig.update_layout(height= h, margin = dict(l = 20 , r = 20),legend_orientation="h", dragmode = False )


    def get_fig(self):
        return self.fig