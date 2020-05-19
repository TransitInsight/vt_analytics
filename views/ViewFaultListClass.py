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
    def __init__(self, table_id, fault_code, start_date, end_date, vobc_id):
        self.table_id = table_id
        self.vobc_id = vobc_id
        self.start_date = start_date
        self.end_date = end_date
        self.fault_code = fault_code
        self.__read_base_data()

    def __read_base_data(self):
        self.fc_df = vobcfault_m.get_fault_list(self.start_date, self.end_date, self.vobc_id, self.fault_code)

    def create_fig(self):
        self.create_vobc_fault_list()

    # add VOBC Fault, shows start time and rectified time
    # regardless actively selected the fault, we already include all fault types
    def create_vobc_fault_list(self):

        if (self.fc_df.empty):
            return

        params = [
            'Weight', 'Torque', 'Width', 'Height',
            'Efficiency', 'Power', 'Displacement'
        ]
        self.__fig = dash_table.DataTable(
            id=self.table_id,
            editable=False,
            columns=(
                [{'id': 'Model', 'name': 'Model'}] +
                [{'id': p, 'name': p} for p in params]
            ),
            data=[
                dict(Model=i, **{param: 0 for param in params})
                for i in range(1, 5)
            ]
        )

    def update_figure_layout(self):
        ytitle = "Velocity (VOBC={})".format(self.vobc_id)
        self.__fig.update_yaxes(title_text=ytitle, showspikes=True)
        self.__fig.update_layout(height=300, margin=dict(l=20, r=20, t=30, b=20),legend_orientation="h")

    def get_fig(self):
        return self.__fig