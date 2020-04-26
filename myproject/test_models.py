

#%%
import unittest
import models.vobcfault_m as vobcDA
import pandas as pd
from datetime import datetime
from datetime import timedelta
import requests
import json
import pprint
#%%
'2020-04-25T00:13:26.017995'
'2015-01-01T00:00:00'

'2015-01-16'

class TestVOBC(unittest.TestCase):

    def test_get_count_by_fc(self):
        df_all = vobcDA.get_count_by('00. All', '2015-01-01T00:00:00', '2020-04-25T00:13:26.017995')
        df_one = vobcDA.get_count_by('03. FAR Level 3 Fault', '2015-01-01T00:00:00', '2020-04-25T00:13:26.017995')
        self.assertTrue( df_all['FaultCount'].count() > 0 )
        self.assertTrue( df_one['FaultCount'].count() > 0 )
        self.assertTrue( df_all['FaultCount'].count() > df_one['FaultCount'].count() )

    def test_get_count_by_fc_date(self):
        end  = datetime(2015,1,1)
        start = end - timedelta(days=100)
        df_all = vobcDA.get_count_by('00. All', start, end)
        self.assertTrue( df_all['FaultCount'].count() > 0 )


    # def test_dt_convert(self):
    #     dtStr = '2014-01-01T00:00:00'
    #     dt = datetime.strptime(dtStr, '%Y-%m-%d H:%M:%S')
    #     self.assertTrue( type(dt) is str )


    def test_runquery(self):
        df = vobcDA.run_query("SELECT faultName, loggedAt, velocity from dlr_vobc_fault where loggedAt >= '2014-01-01T00:00:00' and loggedAt < '2015-04-25T00:13:26.017995' LIMIT 2000 ")
        self.assertTrue( df['loggedAt'].count() > 1000 )

    def test_get_count_by_daterange(self):
        df1 = vobcDA.get_count_by('00. All', '2014-01-01T00:00:00', '2014-04-25T00:13:26.017995')
        df2 = vobcDA.get_count_by('00. All', '2014-01-01T00:00:00', '2014-05-25T00:13:26.017995')
        self.assertTrue( df1['FaultCount'].count() > 0 )
        self.assertTrue( df2['FaultCount'].count() > 0 )
        self.assertTrue( df1['FaultCount'].count() < df2['FaultCount'].count() )

    def test_get_count_by_fc_one(self):
        df = vobcDA.get_count_by('03. FAR Level 3 Fault', '2015-01-06', '2020-04-25T00:13:26.017995')
        self.assertTrue( df['FaultCount'].count() > 0 )

    def test_get_fc(self):
        df = vobcDA.get_all_fault()
        self.assertTrue(df['faultName'].count() == 15)

    def test_isupper(self):
        self.assertTrue('FOO'.isupper())
        self.assertFalse('Foo'.isupper())

    def test_split(self):
        s = 'hello world'
        self.assertEqual(s.split(), ['hello', 'world'])
        # check that s.split fails when the separator is not a string
        with self.assertRaises(TypeError):
            s.split(2)

if __name__ == '__main__':
    unittest.main()

# %%
