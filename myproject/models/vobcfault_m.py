#%%
import myproject.config as cfg
import pandas as pd
from es.elastic.api import connect

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


def get_count_by_fc(fault_name):
    if (fault_name.startswith('00') ):
        return get_count()

    conn = connect(host=cfg.ElasticSearchDS["host"], port=cfg.ElasticSearchDS["port"])
    curs = conn.cursor()

    query = "SELECT faultName, vobcid, count(*) from dlr_vobc_fault where loggedAt > '2015-01-01T12:10:30Z' and loggedAt < '2015-02-02T12:10:30Z' and faultName = '%s' group by faultName, vobcid  LIMIT 10000" % fault_name
    curs.execute(query)
    df = pd.DataFrame(curs, columns =['FaultName', 'VOBCID', 'FaultCount']) 
    return df

#df = get_count_by_vobc_fc()
# df = get_count_by_fc('03. FAR Level 3 Fault')
# df = get_faultname()
# print (df.describe())


# %%
