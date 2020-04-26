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

def get_count_by(fault_name, start_date, end_date):
    fault_condition = ''
    if (not fault_name.startswith('00') ):
        fault_condition = " and faultName = '{}'".format(fault_name)

    if (type(start_date) is datetime):
        start_date = start_date.strftime("%Y-%m-%dT%H:%M:%S")
    if (type(end_date) is datetime):
        end_date = end_date.strftime("%Y-%m-%dT%H:%M:%S")

    query = ("SELECT faultName, vobcid as VOBCID, count(*) as FaultCount"
             " from dlr_vobc_fault "
             " where vobcid <= 300 and loggedAt >= '{}' and loggedAt < '{}' {} "
             " group by faultName, vobcid "
             " LIMIT 10000 ").format( start_date, end_date, fault_condition)

    
    df = run_query(query)
    return df

def get_all_fault():
    query = "SELECT faultName, count(*) as FaultCount from dlr_vobc_fault group by faultName LIMIT 50"
    df = run_query(query)
    return df

def get_count_trend(fault_name, start_date, end_date):
    fault_condition = ''
    if (not fault_name.startswith('00') ):
        fault_condition = " and faultName = '{}'".format(fault_name)    

    if (type(start_date) is datetime):
        start_date = start_date.strftime("%Y-%m-%dT%H:%M:%S")
    if (type(end_date) is datetime):
        end_date = end_date.strftime("%Y-%m-%dT%H:%M:%S")

    query = ("SELECT faultName, loggedDate as LoggedDate, count(*) as FaultCount"
            " from dlr_vobc_fault"
            " where vobcid <=300 and loggedAt >= '{}' and loggedAt < '{}' {}" 
            " group by faultName, loggedDate  LIMIT 5000").format(start_date, end_date, fault_condition)
    df = run_query(query)
    return df

# %%
