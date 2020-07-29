
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
from app import app

import math
import numpy as np
import pandas as pd
import plotly.offline as pyo
import plotly.express as px
import plotly.graph_objs as go
import dash as dash
#import index 

from datetime import datetime as dt
from datetime import timedelta
import re
import multiprocessing as mp

#from modules import module_switch as ms
import json
import requests
import util as util
from elasticsearch import Elasticsearch
from elasticsearch import helpers

def get_switchId(start_date, end_date):
    start_date, end_date  = util.date2str2(start_date, end_date )
    query = ("SELECT switchId from dlr_switch_move where loggedAt >= '{}' and loggedAt < '{}' "
    " group by switchId").format(start_date, end_date)
    L = util.run_query(query)
    L = L["switchId"].tolist()
    return L


def get_switch_delays(switchId, start, end):
    query = ("SELECT HISTOGRAM(loggedAt, INTERVAL 1 HOUR) as h, MAX(moved_t) as max from cmd_to_switch"
    " where switchId = {} and loggedAt >= '{}' and loggedAt <= '{}' and moved_t > 0  group by h").format(switchId, start, end)
    df = util.run_query(query)
    if df.empty:
        return
    if df.empty == False:
        df = df.set_index("h")
        df = df.between_time("6:00", "23:00")
    #df = df.reset_index()
    return df

def get_switch_amts(switchId, startDate, endDate):
    query = ( "SELECT HISTOGRAM(Dates, INTERVAL 1 HOUR) as h, SUM(amt) as amtsum from switch_self_move" 
    " where switchId = {} and Dates >= '{}' and Dates <= '{}' and amt > 0" 
    " group by h").format(switchId, startDate, endDate )
    df = util.run_query(query)
    if df.empty:
        return
    if df.empty == False:
        df = df.set_index("h")
        df = df.between_time("6:00", "23:00")
    #df = df.reset_index()
    return df
    
def gen_unlock_counts_by_hour( switchId, start_date, end_date): 
    start_date, end_date  = util.date2str2(start_date, end_date )
    query = ("SELECT HISTOGRAM(loggedAt, INTERVAL 1 HOUR) as h, COUNT(*) as count"
    " from dlr_switch_move where interval > 0 and loggedAt >= '{}' and loggedAt <= '{}' and switchId = {}"
    " and intervalDesc in ('Moving Time to Left', 'Moving Time to Right' ) and duration >= 10 "
    " group by h").format(start_date, end_date, switchId)

    df = util.run_query(query)
    if df.empty == False:
        df = df.set_index("h")
        df = df.between_time("6:00", "23:00")
        df = df.rename(columns={'count': 'unlock_cnts'})
    return df

def gen_cmd_delay_df(switchId, startDate, endDate):
    data = pd.DataFrame()
    while startDate < endDate:
        end = startDate + timedelta(days=30)
        start_, end_  = util.date2str2(startDate, end)
        df = get_switch_delays(switchId, start_, end_)
        data = data.append(df)
        startDate = end
    return data

def gen_switch_amts_df(switchId, startDate, endDate):
    data = pd.DataFrame()
    while startDate < endDate:
        end = startDate + timedelta(days = 60)
        start_, end_  = util.date2str2(startDate, end)
        df = get_switch_amts(switchId, start_, end_)
        data = data.append(df)
        startDate = end
    return data


def gen_combined_df(switchId, startDate, endDate):
    df_switch_cnts = gen_switch_amts_df(switchId, startDate, endDate)
    df_cmd_delay = gen_cmd_delay_df(switchId, startDate, endDate)
    df_unlock_cnts = gen_unlock_counts_by_hour(switchId, startDate, endDate)

    if df_switch_cnts is None or df_cmd_delay is None:
        return 
    if df_switch_cnts.empty == True or df_cmd_delay.empty == True:
        return  

    df = df_switch_cnts.join(df_cmd_delay)
    if df_unlock_cnts.empty == False:
        df = df.join(df_unlock_cnts)
    else:
        df["unlock_cnts"] = 0 

    df = df.fillna(value = 0)

    df["switchId"] = switchId
    df = df.reset_index()
    df = df.rename(columns={'h': 'loggedAt', 'amtsum': 'switching_cnts','max':'max_time'})
    return df 

def insertDataframeIntoElastic(dataFrame,index='index', typ = 'test', server = 'http://localhost:9200',
                           chunk_size = 2500):
    headers = {'content-type': 'application/x-ndjson', 'Accept-Charset': 'UTF-8'}
    records = dataFrame.to_dict(orient='records')
    actions = ["""{ "index" : { "_index" : "%s", "_type" : "%s"} }\n""" % (index, typ) +json.dumps(records[j])
                    for j in range(len(records))]
    i=0
    while i<len(actions):
        serverAPI = server + '/_bulk' 
        data='\n'.join(actions[i:min([i+chunk_size,len(actions)])])
        data = data + '\n'
        requests.post(serverAPI, data = data, headers=headers)
        #print (r.content)
        i = i+chunk_size




def upload_ELsearch(switchId, startDate, endDate):
    df = gen_combined_df(switchId, startDate, endDate)
    if df is None:
        return
    if df.empty == True:
        return 
    df["loggedAt"] = df["loggedAt"].apply(lambda x: x.isoformat())
    insertDataframeIntoElastic(df, "lin_regression_data")
    print(switchId)
    return df 
    


if __name__ == "__main__":
    start_date = dt(2014, 1, 1)
    end_date = dt(2015, 12, 31)
    
    switches = get_switchId(start_date, end_date)
    df = pd.DataFrame()
    pool = mp.Pool(6)
    
    df.append(pool.starmap(upload_ELsearch, [(i, start_date, end_date) for i in switches]))


    pool.close()

    # df = gen_combined_df(101, start_date, end_date)
    # print(df)

    # df = gen_unlock_counts_by_hour(101, start_date, end_date)
    # print(df)
    # df = gen_switch_amts_df(101, start_date, end_date)
    # df = gen_switch_amts_df(101, start_date, end_date)
    # print(df)

    # df['loggedAt'] = df['loggedAt'].astype(str)
    # insertDataframeIntoElastic(df, "lin_regression_data")





# import dash_core_components as dcc
# import dash_html_components as html
# import dash_bootstrap_components as dbc
# from dash.dependencies import Input, Output, State
# from app import app

# import math
# import numpy as np
# import pandas as pd
# import plotly.offline as pyo
# import plotly.express as px
# import plotly.graph_objs as go
# import dash as dash
# #import index 

# from datetime import datetime as dt
# from datetime import timedelta
# import re
# import multiprocessing as mp

# #from modules import module_switch as ms
# import json
# import requests
# import util as util
# from elasticsearch import Elasticsearch
# from elasticsearch import helpers

# def get_switchId(start_date, end_date):
#     start_date, end_date  = util.date2str2(start_date, end_date )
#     query = ("SELECT switchId from dlr_switch_move where loggedAt >= '{}' and loggedAt < '{}' "
#     " group by switchId").format(start_date, end_date)
#     L = util.run_query(query)
#     L = L["switchId"].tolist()
#     return L


# def get_switch_delays(switchId, start, end):
#     query = ("SELECT * from cmd_to_switch where switchId = {} and loggedAt >= '{}' and loggedAt <= '{}' and moved_t > 0 ").format(switchId, start, end)
#     df = util.run_query(query)
#     if df.empty:
#         return
#     df = df.set_index("loggedAt")
#     df = df.between_time("6:00", "23:00")
#     df = df.reset_index()
#     return df


# def gen_cmd_delay_df(switchId, startDate, endDate):
#     data = pd.DataFrame()
#     while startDate < endDate:
#         end = startDate + timedelta(days=10)
#         start_, end_  = util.date2str2(startDate, end)
#         df = get_switch_delays(switchId, start_, end_)
#         data = data.append(df, ignore_index=True)
#         startDate = end
#     return data


# def get_switch_amts(switchId, startDate, endDate):
#     query = ("SELECT * from switch_self_move where switchId = {} and Dates >= '{}' and Dates <= '{}' and amt > 0 order by amt desc").format(switchId, startDate, endDate )
#     df = util.run_query(query)
#     if df.empty:
#         return
#     df = df.set_index("Dates")
#     df = df.between_time("6:00", "23:00")
#     df = df.reset_index()
#     return df

# def gen_switch_amts_df(switchId, startDate, endDate):
#     data = pd.DataFrame()
#     while startDate < endDate:
#         end = startDate + timedelta(days = 45)
#         start_, end_  = util.date2str2(startDate, end)
#         df = get_switch_amts(switchId, start_, end_)
#         data = data.append(df, ignore_index=True)
#         startDate = end
#     return data

# def gen_unlock_counts_by_hour( switchId, start_date, end_date): 
#     start_date, end_date  = util.date2str2(start_date, end_date )
#     query = ("SELECT HISTOGRAM(loggedAt, INTERVAL 1 HOUR) as h, COUNT(*) as count"
#     " from dlr_switch_move where interval > 0 and loggedAt >= '{}' and loggedAt <= '{}' and switchId = {}"
#     " and intervalDesc in ('Moving Time to Left', 'Moving Time to Right' ) and duration >= 10 "
#     " group by h").format(start_date, end_date, switchId)

#     L = util.run_query(query)
#     return L

# def gen_combined_df(switchId, startDate, endDate):
#     df_switch_cnts = gen_switch_amts_df(switchId, startDate, endDate)
#     #start_, end_  = util.date2str2(startDate, endDate)
#     df_cmd_delay = gen_cmd_delay_df(switchId, startDate, endDate)
#     df_unlock_cnts = gen_unlock_counts_by_hour(switchId, startDate, endDate)

#     if df_switch_cnts is None or df_cmd_delay is None:
#         return 
#     if df_switch_cnts.empty == True or df_cmd_delay.empty == True:
#         return  

#     loggedtime = []
#     amtsum = []
#     move_t_max = []
#     unlock_cnts = []
#     if df_unlock_cnts.empty == False:
#         while startDate < endDate:
#             end = startDate + timedelta(hours=1)
#             x = df_switch_cnts[(startDate < df_switch_cnts["Dates"])&(df_switch_cnts["Dates"] <= end)]
#             y = df_cmd_delay[(startDate < df_cmd_delay["loggedAt"])&(df_cmd_delay["loggedAt"] <= end)]   
#             z = df_unlock_cnts[(startDate < df_unlock_cnts["h"])&(df_unlock_cnts["h"] <= end)]     
#             if x.empty == False and y.empty == False:
#                 loggedtime.append(startDate.isoformat()) 
#                 amtsum.append(x["amt"].sum())
#                 move_t_max.append(y["moved_t"].max())
#                 if z.empty == False:
#                     unlock_cnts.append(z["count"])
#                 else:
#                     unlock_cnts.append(0)
                
#             startDate = end

#     else:
#         while startDate < endDate:
#             end = startDate + timedelta(hours=1)
#             x = df_switch_cnts[(startDate < df_switch_cnts["Dates"])&(df_switch_cnts["Dates"] <= end)]
#             y = df_cmd_delay[(startDate < df_cmd_delay["loggedAt"])&(df_cmd_delay["loggedAt"] <= end)]      
#             if x.empty == False and y.empty == False:
#                 loggedtime.append(startDate.isoformat()) 
#                 amtsum.append(x["amt"].sum())
#                 move_t_max.append(y["moved_t"].max())
#                 unlock_cnts.append(0)
#             startDate = end

#     d = {'loggedAt': loggedtime, 'SelfMoveSum': amtsum, 'MaxMoveTime' : move_t_max}
#     df = pd.DataFrame(data = d)
#     df["switchId"] = switchId
#     df["unlock_cnt"] = unlock_cnts
#     return df 

# def insertDataframeIntoElastic(dataFrame,index='index', typ = 'test', server = 'http://localhost:9200',
#                            chunk_size = 2500):
#     headers = {'content-type': 'application/x-ndjson', 'Accept-Charset': 'UTF-8'}
#     records = dataFrame.to_dict(orient='records')
#     actions = ["""{ "index" : { "_index" : "%s", "_type" : "%s"} }\n""" % (index, typ) +json.dumps(records[j])
#                     for j in range(len(records))]
#     i=0
#     while i<len(actions):
#         serverAPI = server + '/_bulk' 
#         data='\n'.join(actions[i:min([i+chunk_size,len(actions)])])
#         data = data + '\n'
#         requests.post(serverAPI, data = data, headers=headers)
#         #print (r.content)
#         i = i+chunk_size




# def upload_ELsearch(switchId, startDate, endDate):
#     df = gen_combined_df(switchId, startDate, endDate)
#     df['loggedAt'] = df['loggedAt'].astype(str)
#     df = df.to_json()
#     insertDataframeIntoElastic(df, "lin_regression_data_2")
#     print(switchId)
#     return df 
    


# if __name__ == "__main__":
#     start_date = dt(2014, 1, 1)
#     end_date = dt(2014, 2, 28)
#     switches = get_switchId(start_date, end_date)
#     df = pd.DataFrame()
#     pool = mp.Pool(6)
    
#     df.append(pool.starmap(upload_ELsearch, [(i, start_date, end_date) for i in switches]))


#     pool.close()