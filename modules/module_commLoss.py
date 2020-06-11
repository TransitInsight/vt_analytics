import config as cfg
import pandas as pd
from datetime import datetime
import requests
import json
import util as util

def get_commLoss_by_vobcid_loc(start_date, end_date, velocity_dropdown = None, apstatus = None, commtype = None):
    
    start_date,end_date = util.date2str2(start_date,end_date)
    veld = ''
    apstat = ''
    commT = ''
    if velocity_dropdown is 0: 
        veld = " and velocity = 0"
    if velocity_dropdown is 1: 
        veld = " and NOT(velocity = 0)"
    if apstatus is 1: 
        apstat = " and activePassiveStatus = true"
    if apstatus is 0: 
        apstat = " and activePassiveStatus = false"
    if commtype is not None and commtype != -1:
        commT = " and commType = {}".format(commtype)
 

    query = ("SELECT vobcid, locationName, count(commType) as commLossCount from dlr_vobc_comloss"
                " where commType > 0 and commType < 6 and loggedAt >= '{}' and loggedAt < '{}' {} {} {}" 
                " group by vobcid, locationName"
                " order by commLossCount desc"
                " LIMIT 300").format(start_date, end_date, veld, apstat, commT)

    
    df = util.run_query(query)
    if df is None:
        df = pd.DataFrame() 
    return df

def get_commLoss_by_vobcid_loc_date(start_date, end_date, vobcid, location, velocity_dropdown = None, apstatus = None, commtype = None):
    
    vobcs = ''
    loc = ''
    veld = ''
    apstat = ''
    commT = ''
    if (vobcid != -1 ):
        vobcs = " and vobcid = {}".format(vobcid)    
    if (location is not None ):
        loc = " and locationName = '{}'".format(location)   
    if velocity_dropdown is 0: 
        veld = " and velocity = 0"
    if velocity_dropdown is 1: 
        veld = " and NOT(velocity = 0)"
    if apstatus is 1: 
        apstat = " and activePassiveStatus = true"
    if apstatus is 0: 
        apstat = " and activePassiveStatus = false"
    if commtype is not None and commtype != -1: 
        commT = " and commType = {}".format(commtype)

    start_date,end_date = util.date2str2(start_date,end_date)
    
    query = ("SELECT HISTOGRAM(loggedAt, INTERVAL 1 DAY) as date, count(*) as commLossCount" 
            " from dlr_vobc_comloss" 
            " where commType > 0 and commType < 6 and loggedAt >= '{}' and loggedAt < '{}' {} {} {} {} {}" 
            " GROUP BY date").format(start_date, end_date, vobcs, loc, veld, apstat, commT)
    
    df = util.run_query(query)

    return df

def get_commLoss_list(start_date,end_date, vobc_id = None, location = None, velocity= None, apstatus = None, commtype = None):
    start_date,end_date = util.date2str2(start_date,end_date)
    query = "SELECT vobcid, parentTrainId, loggedAt, velocity, activePassiveStatus, locationName, commType from dlr_vobc_comloss where commType > 0 and commType < 6 and loggedAt >= '{}' and loggedAt < '{}'".format(start_date,end_date)

    if vobc_id is not None and vobc_id != -1:
        query += " and vobcid = {}".format(vobc_id)
    if (location is not None ):
        query += " and locationName = '{}'".format(location)
    if velocity is 0: 
        query += " and velocity = 0"
    if velocity is 1: 
        query += " and NOT(velocity = 0)"
    if apstatus is 1: 
        query += " and activePassiveStatus = true"
    if apstatus is 0: 
        query += " and activePassiveStatus = false"
    if commtype is not None and commtype != -1: 
        query += " and commType = {}".format(commtype)

    df = util.run_query(query)
    
    if df is None:
        df = pd.DataFrame() 

    return df