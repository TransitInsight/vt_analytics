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

    if (type(start_date) is datetime):
        start_date = start_date.strftime("%Y-%m-%dT%H:%M:%S")
    if (type(end_date) is datetime):
        end_date = end_date.strftime("%Y-%m-%dT%H:%M:%S")

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

def get_fault_list(start_date,end_date, vobc_id):
    start_date,end_date = util.date2str2(start_date,end_date)
    query = "SELECT faultName, faultCode, loggedAt, velocity from dlr_vobc_fault where loggedAt >= '{}' and loggedAt < '{}' and vobcid = {}".format(start_date,end_date, vobc_id)
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

    if (type(start_date) is datetime):
        start_date = start_date.strftime("%Y-%m-%dT%H:%M:%S")
    if (type(end_date) is datetime):
        end_date = end_date.strftime("%Y-%m-%dT%H:%M:%S")

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

    dt_str = numpy.datetime_as_string(df['fcStart'][0].to_datetime64(), unit='s')

    return dateparser.parse(dt_str)