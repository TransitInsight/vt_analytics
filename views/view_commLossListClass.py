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

from modules import module_commLoss 
import config as cfg
import util as util
import pandas as pd
import plotly.graph_objs as go



class ViewCommLossListClass:
    def __init__(self, table_id, start_date, end_date, vobc_id, location = None, velcocity_dropdown = None, apstatus = None, commLoss = None):
        self.table_id = table_id
        self.vobc_id = vobc_id
        self.start_date = start_date
        self.end_date = end_date
        self.location = location
        self.velocity_dropdown = velcocity_dropdown
        self.apstatus = apstatus
        self.commLoss = commLoss
        self.__read_base_data()
        
    def __read_base_data(self):
        df = module_commLoss.get_commLoss_list(self.start_date, self.end_date, self.vobc_id, self.location, self.velocity_dropdown, self.apstatus, self.commLoss)

        self.df = df

    def create_fig(self):
        self.create_vobc_fault_list()

    def create_vobc_fault_list(self):
        if len(self.df.index) == 0:
            return

        self.__fig = dash_table.DataTable(
            id=self.table_id,
            page_size=6,
            editable=False,
            columns=(
                [
                    {'id': 'loggedAt', 'name': 'Logged At'},
                    {'id': 'vobcid', 'name': 'VOBC'},
                    {'id': 'parentTrainId', 'name': 'PVOBC'},
                    {'id': 'commType', 'name': 'commType'},
                    {'id': 'velocity', 'name': 'Vel'},
                    {'id': 'locationName', 'name': 'Location'},
                    {'id': 'activePassiveStatus', 'name': 'VOBC Act'},
                ] 
            ),
            data=self.get_data()
        )

    def get_data(self):
        return self.df.to_dict('rows')

    def get_fig(self):
        return self.__fig