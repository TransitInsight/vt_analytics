#%%
import myproject.config as cfg
import pandas as pd
from es.elastic.api import connect
from datetime import datetime

#%%

def get_count():
    conn = connect(host=cfg.ElasticSearchDS["host"], port=cfg.ElasticSearchDS["port"])
    curs = conn.cursor()
    curs.execute("SELECT faultName, vobcid, count(*) from dlr_vobc_fault where loggedAt > '2015-01-01T12:10:30Z' and loggedAt < '2015-02-02T12:10:30Z' group by faultName, vobcid  LIMIT 10000")
    df = pd.DataFrame(curs, columns =['FaultName', 'VOBCID', 'FaultCount']) 
    return df

def get_faultname():
    conn = connect(host=cfg.ElasticSearchDS["host"], port=cfg.ElasticSearchDS["port"])
    curs = conn.cursor()
    curs.execute("SELECT faultName, count(*) faultName from dlr_vobc_fault group by faultName")
    df = pd.DataFrame(curs, columns =['FaultName', 'FaultCount']) 
    return df


def get_count_by_fc(fault_name, start_date, end_date):
    fault_condition = ''
    if (not fault_name.startswith('00') ):
        fault_condition = " and faultName = '{}'".format(fault_name)
#2014-01-01T00:00:00
    if (type(start_date) is datetime):
        start_date = start_date.strftime("%Y-%m-%dT%H:%M:%S")
    if (type(end_date) is datetime):
        end_date = end_date.strftime("%Y-%m-%dT%H:%M:%S")

    conn = connect(host=cfg.ElasticSearchDS["host"], port=cfg.ElasticSearchDS["port"])
    curs = conn.cursor()

    query = ("SELECT faultName, vobcid, count(*)"
             " from dlr_vobc_fault "
             " where loggedAt >= '{}' and loggedAt < '{}' {} "
             " group by faultName, vobcid "
             " LIMIT 10000 ").format( start_date, end_date, fault_condition)

    curs.execute(query)
    df = pd.DataFrame(curs, columns =['FaultName', 'VOBCID', 'FaultCount']) 
    return df

#%%



#%%


#df = get_count_by_vobc_fc()
# df = get_count_by_fc('03. FAR Level 3 Fault')
# df = get_faultname()
# print (df.describe())


# %%
