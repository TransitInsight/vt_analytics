
#%%
from datetime import datetime
from datetime import timedelta
import dateparser
import requests
import pandas as pd
import myproject.config as cfg
import json
import re
import random
import numpy as np

#%%
def date2str1(op_date):
    if (type(op_date) is datetime):
        op_date = op_date.strftime("%Y-%m-%dT%H:%M:%S")

    return op_date

def date2str2(start_date, end_date):
    start_date = date2str1(start_date)
    end_date = date2str1(end_date)

    return start_date, end_date

def str2date1(op_date):
    if isinstance(op_date, str):
        op_date = dateparser.parse(op_date)

    return op_date

def run_query(query):
    return run_query_in_memory(query)
    # if cfg.ElasticSearchDS['in_memory']:
    #     df = run_query_in_memory(query)
    # else:
    #     df = run_query_es(query)
    # return df


def run_query_es(query):
    headers = {'Content-Type': 'application/json'}

    query = {
        "query": query,
        "fetch_size": cfg.es_fetch_size
    }

    response = requests.post(cfg.ElasticSearchDS['sqlurl'], headers=headers, data=json.dumps(query))
    if (response.status_code != 200):
        return None

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

def run_query_in_memory(query):
    return_size = 200

    tokens = re.split(' |,', query)
    tokens = list(filter(None, tokens))

    fields = []
    isField = False
    i = 0
    while i < len(tokens):
        item = tokens[i]
        if item.lower() == 'from': isField = False
        if len(item) > 0 and isField and tokens[i+1].lower() != 'as' and item.lower() != 'as':
            fields.append(item.rstrip())
        if item.lower() == 'select': isField = True
        i += 1

    df = pd.DataFrame()
    
    time_list = [np.datetime64(datetime.today() - timedelta(days=x)) for x in range(return_size)]
    date_list = [np.datetime64((datetime.today() - timedelta(days=x)).date()) for x in range(return_size)]

    fc_list = [] 
    fc_name_list = []
    i = 0
    while i < return_size:
        r = random.randint(1, 15)
        fc_list.append(r)
        fc_name_list.append('fc{}:random text'.format(r))
        i += 1
    
    for field in fields:
        if 'loggedat' in field.lower() or 'fcstart' in field.lower():
            df[field] = time_list
        elif 'loggeddate' in field.lower():
            df[field] = date_list
        elif 'id' in field.lower() or 'code' in field.lower() or 'count' in field.lower():
            df[field] = fc_list
        else:
            df[field] = fc_name_list
            df[field] = pd.Series(df[field], dtype=pd.StringDtype())


    return  df
