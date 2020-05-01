#%%
import myproject.config as cfg
import pandas as pd
from datetime import datetime
import requests
import json
import myproject.util as util

#%%

def get_count_by(fault_code, start_date, end_date):
    fault_condition = ''
    if (fault_code != -1):
        fault_condition = " and faultCode = {}".format(fault_code)

    if (type(start_date) is datetime):
        start_date = start_date.strftime("%Y-%m-%dT%H:%M:%S")
    if (type(end_date) is datetime):
        end_date = end_date.strftime("%Y-%m-%dT%H:%M:%S")

    query = ("SELECT faultName, faultCode, vobcid as VOBCID, count(*) as FaultCount"
             " from dlr_vobc_fault "
             " where vobcid <= 300 and loggedAt >= '{}' and loggedAt < '{}' {} "
             " group by faultName, faultCode, vobcid "
             " LIMIT 10000 ").format( start_date, end_date, fault_condition)
    
    df = util.run_query(query)
    return df
