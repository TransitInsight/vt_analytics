#%%
import config as cfg
import pandas as pd
from datetime import datetime
import json
import util as util
import numpy
import dateparser

#%%

def get_count_by(fault_code, start_date, end_date, velocity = None, apstatus = None):
    fault_condition = ''
    apstat =''
    vel = ''
    if (fault_code != -1):
        fault_condition = " and faultCode = {}".format(fault_code)
    if velocity is 0: 
        vel += " and velocity = 0"
    if velocity is 1: 
        vel += " and NOT(velocity = 0)"
    if apstatus is 1: 
        apstat += " and activePassiveStatus = true"
    if apstatus is 0: 
        apstat += " and activePassiveStatus = false"
    start_date,end_date = util.date2str2(start_date,end_date)

    query = ("SELECT faultName, faultCode, vobcid as VOBCID, count(*) as FaultCount"
             " from dlr_vobc_fault "
             " where vobcid <= 300 and faultCodeSet = True and loggedAt >= '{}' and loggedAt < '{}' {} {} {} "
             " group by faultName, faultCode, vobcid "
             " LIMIT 10000 ").format( start_date, end_date, fault_condition, vel, apstat)
    
    df = util.run_query(query)
    return df

def get_all_fault():
    query = "SELECT faultName, faultCode, count(*) as FaultCount from dlr_vobc_fault group by faultName, faultCode LIMIT 50"
    df = util.run_query(query)
    return df

def get_fault_list(start_date,end_date, vobc_id = None, faultCode = None, location = None, velocity= None, apstatus = None):
    start_date,end_date = util.date2str2(start_date,end_date)
    query = "SELECT vobcid, parentTrainId, faultName, faultCode, loggedAt, velocity, faultCodeSet, activePassiveStatus, locationName from dlr_vobc_fault where loggedAt >= '{}' and loggedAt < '{}'".format(start_date,end_date)

    if vobc_id is not None and vobc_id != -1:
        query += " and vobcid = {}".format(vobc_id)
    if faultCode is not None and faultCode != 0 and faultCode != -1:
        query += " and faultCode = {}".format(faultCode)
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


    df = util.run_query(query)
    return df

def get_count_trend(fault_code, start_date, end_date, vobcid, velocity = None, apstatus = None):
    fault_condition = ''
    vobc_condition = ''
    veld = ''
    apstat = ''
    if (fault_code != -1 ):
        fault_condition = " and faultCode  = {}".format(fault_code)    
    if (vobcid != -1 ):
        vobc_condition = " and vobcid = {}".format(vobcid)     
    if velocity is 0: 
        veld = " and velocity = 0"
    if velocity is 1: 
        veld = " and NOT(velocity = 0)"
    if apstatus is 1: 
        apstat = " and activePassiveStatus = true"
    if apstatus is 0: 
        apstat = " and activePassiveStatus = false"

    query = ("SELECT faultName, faultCode, loggedDate as LoggedDate, count(*) as FaultCount"
            " from dlr_vobc_fault"
            " where vobcid <=300 and faultCodeSet = True and loggedAt >= '{}' and loggedAt < '{}' {} {} {} {}" 
            " group by faultName, faultCode, loggedDate  LIMIT 5000").format(start_date, end_date, fault_condition, vobc_condition, veld, apstat)
    df = util.run_query(query)
    return df

def get_count_location(fault_code, start_date, end_date, vobcid):
    fault_condition = ''
    vobc_condition = ''
    if (fault_code != -1 ):
        fault_condition = " and faultCode  = {}".format(fault_code)    
    if (vobcid != -1 ):
        vobc_condition = " and vobcid = {}".format(vobcid)    

    start_date,end_date = util.date2str2(start_date,end_date)

    query = ("SELECT faultName, faultCode, locationName as LocationName, count(*) as FaultCount"
            " from dlr_vobc_fault"
            " where vobcid <=300 and loggedAt >= '{}' and loggedAt < '{}' {} {}" 
            " group by faultName, faultCode, locationName  LIMIT 5000").format(start_date, end_date, fault_condition, vobc_condition)
    df = util.run_query(query)
    return df

def create_dropdown_options():
    fc_options = [{'label':y, "value":x} for x,y in cfg.vobc_fault_name_dict.items()]
    return fc_options

def get_fault_name(fault_code):
    return cfg.vobc_fault_name_dict[fault_code]

def get_first_fault_time(op_date, fault_code, vobc_id):
    op_date = util.str2date1(op_date)

    query = ("SELECT min(loggedAt) as fcStart"
            " from dlr_vobc_fault"
            " where faultCode = {} and vobcid ={} and loggedDate = '{}'").format(fault_code, vobc_id,  op_date.date())

    df = util.run_query(query)

    if (df is None):
        return op_date
        
    dt_str = numpy.datetime_as_string(df['fcStart'][0].to_datetime64(), unit='s')

    return dateparser.parse(dt_str)

def get_faultcount_by_vobcid_loc(start_date, end_date,fault_code, velocity_dropdown = None, apstatus = None ):
    
    start_date,end_date = util.date2str2(start_date,end_date)
    faults = ''
    veld = ''
    apstat = ''
    if (fault_code != -1 ):
        faults = " and faultCode  = {}".format(fault_code)   
    if velocity_dropdown is 0: 
        veld = " and velocity = 0"
    if velocity_dropdown is 1: 
        veld = " and NOT(velocity = 0)"
    if apstatus is 1: 
        apstat = " and activePassiveStatus = true"
    if apstatus is 0: 
        apstat = " and activePassiveStatus = false"

    query = ("SELECT vobcid, locationName, count(vobcid) as FaultCount from dlr_vobc_fault"
                " where loggedAt >= '{}' and loggedAt < '{}' and faultCodeSet = true {} {} {}" 
                " group by vobcid, locationName"
                " order by FaultCount desc"
                " LIMIT 300").format(start_date, end_date, faults, veld, apstat)
    
    df = util.run_query(query)

    return df

def get_faultcount_by_vobcid_loc_date(start_date, end_date, vobcid, fault_code, location, velocity_dropdown = None, apstatus = None):
    
    faults = ''
    vobcs = ''
    loc = ''
    veld = ''
    apstat = ''
    if (fault_code != -1 ):
        faults = " and faultCode  = {}".format(fault_code)    
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

    start_date,end_date = util.date2str2(start_date,end_date)
    
    query = ("SELECT HISTOGRAM(loggedAt, INTERVAL 1 DAY) as date, count(loggedAt) as FaultCount" 
            " from dlr_vobc_fault" 
            " where loggedAt >= '{}' and loggedAt < '{}' and faultCodeSet = true  {} {} {} {} {}" 
            " GROUP BY date").format(start_date, end_date, vobcs, faults, loc, veld, apstat)
    
    df = util.run_query(query)

    return df