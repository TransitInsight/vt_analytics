import os,sys,inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir) 


#%%
import dash_core_components as dcc
import dash_html_components as html
import dash_table
from datetime import datetime
from datetime import timedelta

from app import app

from modules import module_vobcfault as vobcfault_m
import config as cfg
import util as util
import pandas as pd
import plotly.graph_objs as go



class ViewFaultListClass:
    def __init__(self, table_id, fault_code, start_date, end_date, vobc_id, location = None, velcocity_dropdown = None, apstatus = None):
        self.table_id = table_id
        self.vobc_id = vobc_id
        self.start_date = start_date
        self.end_date = end_date
        self.fault_code = fault_code
        self.location = location
        self.velocity_dropdown = velcocity_dropdown
        self.apstatus = apstatus
        self.__read_base_data()
        

    def __read_base_data(self):
        df = vobcfault_m.get_fault_list(self.start_date, self.end_date, self.vobc_id, self.fault_code, self.location, self.velocity_dropdown, self.apstatus)
        if len(df.index) != 0:
            #df.loggedAt = pd.DatetimeIndex(df.loggedAt).strftime("%Y-%m-%d")
            self.fc_df = df[df['faultCodeSet'] == 1]
        else:
            self.fc_df = df

    def create_fig(self):
        self.create_vobc_fault_list()

    # add VOBC Fault, shows start time and rectified time
    # regardless actively selected the fault, we already include all fault types
    def create_vobc_fault_list(self):
        if len(self.fc_df.index) == 0:
            return
        # display_fc = self.fc_df[['loggedAt', 'vobcid', 'faultName', 'velocity', 'locationName', 'activePassiveStatus']].copy()
        

        self.__fig = dash_table.DataTable(
            id=self.table_id,
            page_size=6,
            editable=False,
            columns=(
                [
                    {'id': 'loggedAt', 'name': 'Logged At'},
                    {'id': 'vobcid', 'name': 'VOBC'},
                    {'id': 'faultName', 'name': 'Fault Name'},
                    {'id': 'velocity', 'name': 'Vel'},
                    {'id': 'locationName', 'name': 'Location'},
                    {'id': 'activePassiveStatus', 'name': 'VOBC Active'},
                    {'id': 'faultCodeSet', 'name': 'Fault Active'}
                ] 
            ),
            data=self.get_data()
        )

    def get_data(self):
        return self.fc_df.to_dict('rows')

    def get_fig(self):
        return self.__fig