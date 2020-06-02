#%%
import config as cfg
import pandas as pd
from datetime import datetime
import requests
import json
import util as util

#%%

def get_trainmove(vobc_id, start_date, end_date):
    start_date, end_date = util.date2str2(start_date,end_date)
    if (vobc_id == None or vobc_id == -1 ):
        return None

    query = ("SELECT activePassiveStatus, loggedAt, loggedDate, loopName, velocity, vobcid, trainId, maximumVelocity, doorCmd, doorStatus"
             " from dlr_train_move "
             " where vobcid = {} and loggedAt >= '{}' and loggedAt < '{}'"
             " order by loggedAt LIMIT 10000 ").format( vobc_id, start_date, end_date)
    
    df = util.run_query(query)

    if df is not None and not df.empty:
        df['doorStatus'] = df['doorStatus'].apply(lambda x: x*10 - 35)
        df['doorCmd'] = df['doorCmd'].apply(lambda x: x*10 - 35)

    return df

def get_unique_vobcid_list(start_date, end_date, trainId):
    if trainId == None or end_date == None or start_date == None:
        return []
    query =("SELECT vobcid from dlr_train_move"
    " where trainId = '{}' and loggedAt >= '{}' and loggedAt < '{}'" 
    " group by vobcid").format(trainId, start_date, end_date)

    df = util.run_query(query)
    return df["vobcid"].to_list()