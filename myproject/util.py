from datetime import datetime
from datetime import timedelta
import requests
import pandas as pd
import myproject.config as cfg
import json


def NormalizeOneDate(op_date):
    if (type(op_date) is datetime):
        op_date = op_date.strftime("%Y-%m-%dT%H:%M:%S")

    return op_date

def NormalizeDate(start_date, end_date):
    start_date = NormalizeOneDate(start_date)
    end_date = NormalizeOneDate(end_date)

    return start_date, end_date


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
