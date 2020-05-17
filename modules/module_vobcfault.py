#%%
import config as cfg
import pandas as pd
from datetime import datetime
import json
import util as util
import numpy
import dateparser

#%%

def get_count_by(fault_code, start_date, end_date):
    fault_condition = ''
    if (fault_code != -1):
        fault_condition = " and faultCode = {}".format(fault_code)

    start_date,end_date = util.date2str2(start_date,end_date)

    query = ("SELECT faultName, faultCode, vobcid as VOBCID, count(*) as FaultCount"
             " from dlr_vobc_fault "
             " where vobcid <= 300 and loggedAt >= '{}' and loggedAt < '{}' {} "
             " group by faultName, faultCode, vobcid "
             " LIMIT 10000 ").format( start_date, end_date, fault_condition)
    
    df = util.run_query(query)
    return df

def get_all_fault():
    query = "SELECT faultName, faultCode, count(*) as FaultCount from dlr_vobc_fault group by faultName, faultCode LIMIT 50"
    df = util.run_query(query)
    return df

def get_fault_list(start_date,end_date, vobc_id = None, faultCode = None):
    start_date,end_date = util.date2str2(start_date,end_date)
    query = "SELECT vobcid, faultName, faultCode, loggedAt, velocity, faultCodeSet from dlr_vobc_fault where loggedAt >= '{}' and loggedAt < '{}'".format(start_date,end_date)

    if vobc_id is not None and vobc_id != -1:
        query += " and vobcid = {}".format(vobc_id)
    if faultCode is not None and faultCode != 0 and faultCode != -1:
        query += " and faultCode = {}".format(faultCode)

    df = util.run_query(query)
    return df

def get_count_trend(fault_code, start_date, end_date, vobcid):
    fault_condition = ''
    vobc_condition = ''
    if (fault_code != -1 ):
        fault_condition = " and faultCode  = {}".format(fault_code)    
    if (vobcid != -1 ):
        vobc_condition = " and vobcid = {}".format(vobcid)    

    start_date,end_date = util.date2str2(start_date,end_date)

    query = ("SELECT faultName, faultCode, loggedDate as LoggedDate, count(*) as FaultCount"
            " from dlr_vobc_fault"
            " where vobcid <=300 and loggedAt >= '{}' and loggedAt < '{}' {} {}" 
            " group by faultName, faultCode, loggedDate  LIMIT 5000").format(start_date, end_date, fault_condition, vobc_condition)
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