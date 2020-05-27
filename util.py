
#%%
from datetime import datetime
from datetime import timedelta
import dateparser
import requests
import pandas as pd
import config as cfg
import json
import re
import random
import numpy as np
import os
import base64
import dash_html_components as html


#%%
def date2str1(op_date):

    if(type(op_date) is str):
        op_date = str2date1(op_date)

    if (type(op_date) is datetime):
        op_date = op_date.strftime("%Y-%m-%dT%H:%M:%S")

    return op_date

# Convert two date to two strings using the format works for Elastic Search
# throw exception if start_date is later than end_date
def date2str2(start_date, end_date):
    start_date = date2str1(start_date)
    end_date = date2str1(end_date)

    if start_date > end_date:
        raise ValueError("start_date needs to be smaller than end_date")

    return start_date, end_date

def str2date1(op_date):
    if op_date is None:
        op_date = '2015-1-1 10:12'
    if isinstance(op_date, str):
        op_date = dateparser.parse(op_date)

    return op_date

def is_in_memory():
    #return True
    return cfg.ElasticSearchDS['in_memory'] or os.name != 'nt'# not on windows, must be linux

# run elastic search query
# when running on Azure DevOP pipline (Linux only), ElasticSearch is not available, it uses generated result
def run_query(query):
    if is_in_memory():
        df = run_query_in_memory(query)
    else:
        df = run_query_es(query)
    return df


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
    
    id_list = list(range(0,return_size))

    time_list = [np.datetime64(datetime.today() - timedelta(days=x)) for x in range(return_size)]
    date_list = [np.datetime64((datetime.today() - timedelta(days=x)).date()) for x in range(return_size)]

    fc_list = [] 
    fc_name_list = []
    status_list = []
    velocity_list =[]
    i = 0
    while i < return_size:
        r = random.randint(1, 15)
        fc_list.append(r)
        fc_name_list.append('fc{}:random text'.format(r))
        status_list.append(random.randint(0,1))
        velocity_list.append(random.randint(0, 80))
        i += 1
    
    for field in fields:
        if 'loggedat' in field.lower() or 'fcstart' in field.lower():
            df[field] = time_list
        elif 'loggeddate' in field.lower():
            df[field] = date_list
        elif 'id' in field.lower() :
            df[field] = id_list
        elif 'code' in field.lower() or 'count' in field.lower():
            df[field] = fc_list
        elif 'doorcmd' in field.lower() :
            df[field] = status_list
            df[field] = df[field].apply(lambda x: x+2) #cmd returns 2, & 3
        elif 'doorstatus' in field.lower() or 'activepassivestatus' in field.lower():
            df[field] = status_list
        elif 'velocity' in field.lower():
            df[field] = velocity_list
        elif 'faultcodeset' in field.lower():
            df[field] = status_list
        else:
            df[field] = fc_name_list
            df[field] = pd.Series(df[field], dtype=pd.StringDtype())


    return  df


### When run UT on Azure pipeline, this ensures use local in-memory DB
def IsInMemoryTrue(ret):
    if is_in_memory():
        return True
    else:
        return ret


def get_logo_img():
    encoded_image=base64.b64encode(open('./ti_logo.png', 'rb').read())

    assert encoded_image is not None, "can't load logo image"

    logoImg = html.Img(src='data:image/png;base64,{}'.format(encoded_image))

    return logoImg