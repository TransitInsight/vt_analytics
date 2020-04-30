#%%
import myproject.config as cfg
import pandas as pd
from datetime import datetime
import requests
import json

#%%

def run_query(query):
    headers = {'Content-Type': 'application/json'}

    query = {
        "query": query,
        "fetch_size": cfg.es_fetch_size
    }

    response = requests.post(cfg.ElasticSearchDS['sqlurl'], headers=headers, data=json.dumps(query))

    df = pd.json_normalize(response.json(),'rows')
    if (df.shape[0] == 0):
        return df
    df.columns = [d['name'] for d in response.json()['columns']]

    for c in response.json()['columns']:
        dtype = None
        if (c['type'] == 'text'):
            dtype = pd.StringDtype()
        elif (c['type'] == 'datetime'):
            dtype = 'datetime64'
        else:
            dtype = None

        if ( not dtype is None ):
            df[c['name']] = pd.Series(df[c['name']], dtype=dtype)

    return df

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
    
    df = run_query(query)
    return df

def get_all_fault():
    query = "SELECT faultName, faultCode, count(*) as FaultCount from dlr_vobc_fault group by faultName, faultCode LIMIT 50"
    df = run_query(query)
    return df

def get_count_trend(fault_code, start_date, end_date, vobcid):
    fault_condition = ''
    vobc_condition = ''
    if (fault_code != -1 ):
        fault_condition = " and faultCode  = {}".format(fault_code)    
    if (vobcid != -1 ):
        vobc_condition = " and vobcid = {}".format(vobcid)    

    if (type(start_date) is datetime):
        start_date = start_date.strftime("%Y-%m-%dT%H:%M:%S")
    if (type(end_date) is datetime):
        end_date = end_date.strftime("%Y-%m-%dT%H:%M:%S")

    query = ("SELECT faultName, faultCode, loggedDate as LoggedDate, count(*) as FaultCount"
            " from dlr_vobc_fault"
            " where vobcid <=300 and loggedAt >= '{}' and loggedAt < '{}' {} {}" 
            " group by faultName, faultCode, loggedDate  LIMIT 5000").format(start_date, end_date, fault_condition, vobc_condition)
    df = run_query(query)
    return df

def get_count_location(fault_code, start_date, end_date, vobcid):
    fault_condition = ''
    vobc_condition = ''
    if (fault_code != -1 ):
        fault_condition = " and faultCode  = {}".format(fault_code)    
    if (vobcid != -1 ):
        vobc_condition = " and vobcid = {}".format(vobcid)    

    if (type(start_date) is datetime):
        start_date = start_date.strftime("%Y-%m-%dT%H:%M:%S")
    if (type(end_date) is datetime):
        end_date = end_date.strftime("%Y-%m-%dT%H:%M:%S")

    query = ("SELECT faultName, faultCode, locationName as LocationName, count(*) as FaultCount"
            " from dlr_vobc_fault"
            " where vobcid <=300 and loggedAt >= '{}' and loggedAt < '{}' {} {}" 
            " group by faultName, faultCode, locationName  LIMIT 5000").format(start_date, end_date, fault_condition, vobc_condition)
    df = run_query(query)
    return df

# %%

def create_dropdown_options():
    fc_options = [{'label':y, "value":x} for x,y in cfg.vobc_fault_name_dict.items()]
    return fc_options

def get_fault_name(fault_code):
    return cfg.vobc_fault_name_dict[fault_code]




