

#%%
import unittest
import myproject.models.vobcfault_m as vobcDA
import myproject.models.trainmove_m as trainmoveDA
import pandas as pd
from datetime import datetime
from datetime import timedelta
import requests
import json
import pprint

import myproject.config as cfg
import myproject.util as util

#%%
'2020-04-25T00:13:26.017995'
'2015-01-01T00:00:00'

'2015-01-16'

class TestVOBC(unittest.TestCase):

    def test_get_count_by_fc(self):
        df_all = vobcDA.get_count_by(-1, '2015-01-01T00:00:00', '2020-04-25T00:13:26.017995')
        df_one = vobcDA.get_count_by(3, '2015-01-01T00:00:00', '2020-04-25T00:13:26.017995')
        self.assertTrue( df_all['FaultCount'].count() > 0 )
        self.assertTrue( df_one['FaultCount'].count() > 0 )
        self.assertTrue( df_all['FaultCount'].count() > df_one['FaultCount'].count() )

    def test_get_count_by_fc_date(self):
        end  = datetime(2015,1,1)
        start = end - timedelta(days=100)
        df_all = vobcDA.get_count_by(-1, start, end)
        self.assertTrue( df_all['FaultCount'].count() > 0 )


    def test_runquery(self):
        df = util.run_query("SELECT faultName, loggedAt, velocity from dlr_vobc_fault where loggedAt >= '2014-01-01T00:00:00' and loggedAt < '2015-04-25T00:13:26.017995' LIMIT 2000 ")
        self.assertTrue( df['loggedAt'].count() > 1000 )

    def test_get_count_by_daterange(self):
        df1 = vobcDA.get_count_by(-1, '2014-01-01T00:00:00', '2014-04-25T00:13:26.017995')
        df2 = vobcDA.get_count_by(-1, '2014-01-01T00:00:00', '2014-05-25T00:13:26.017995')
        self.assertTrue( df1['FaultCount'].count() > 0 )
        self.assertTrue( df2['FaultCount'].count() > 0 )
        self.assertTrue( df1['FaultCount'].count() < df2['FaultCount'].count() )

    def test_get_count_by_fc_one(self):
        df = vobcDA.get_count_by(3, '2015-01-06', '2020-04-25T00:13:26.017995')
        self.assertTrue( df['FaultCount'].count() > 0 )

    def test_get_fc(self):
        df = vobcDA.get_all_fault()
        self.assertTrue(df['faultName'].count() == 15)
        self.assertTrue(df['faultCode'].count() == 15)

    def test_get_fc_list(self):
        df = vobcDA.get_fault_list('2015-01-01T10:00','2015-01-01T20:00', 248)
        self.assertTrue(df['loggedAt'].count() > 0)


    def test_get_fc_trend(self):
        df = vobcDA.get_count_trend(-1, '2014-01-01T00:00:00', '2015-04-25T00:13:26.017995', -1)
        self.assertTrue(df['LoggedDate'].count() > 1000)
        self.assertTrue(len(df['faultName'].unique()) == 15)

        df1 = vobcDA.get_count_trend(3, '2014-01-01T00:00:00', '2015-04-25T00:13:26.017995', -1)
        self.assertTrue(df['LoggedDate'].count() > df1['LoggedDate'].count())


    def test_get_fc_trend1(self):
        df = vobcDA.get_count_trend(-1, '2014-01-01T00:00:00', '2015-04-25T00:13:26.017995', -1)
        self.assertTrue(df['LoggedDate'].count() > 1000)
        self.assertTrue(len(df['faultName'].unique()) == 15)

        df1 = vobcDA.get_count_trend(-1, '2014-01-01T00:00:00', '2015-04-25T00:13:26.017995', 2)
        self.assertTrue(df['LoggedDate'].count() > df1['LoggedDate'].count())


    def test_get_fc_location(self):
        df = vobcDA.get_count_location(-1, '2014-01-01T00:00:00', '2015-04-25T00:13:26.017995', -1)
        self.assertTrue(df['LocationName'].count() > 1000)
        self.assertTrue(len(df['faultName'].unique()) == 15)

        df1 = vobcDA.get_count_trend(-1, '2014-01-01T00:00:00', '2015-04-25T00:13:26.017995', 2)
        self.assertTrue(df['LocationName'].count() > df1['LoggedDate'].count())

    def test_isupper(self):
        self.assertTrue('FOO'.isupper())
        self.assertFalse('Foo'.isupper())

    def test_split(self):
        s = 'hello world'
        self.assertEqual(s.split(), ['hello', 'world'])
        # check that s.split fails when the separator is not a string
        with self.assertRaises(TypeError):
            s.split(2)

    def test_color(self):
        c = cfg.vobc_fault_color_dict[1]
        self.assertTrue(c != None)

        c = cfg.vobc_fault_color_dict[-1]
        self.assertTrue(c != None)

    def test_fcname(self):
        for key, value in cfg.vobc_fault_name_dict.items():
            print(key, ":", value)
        fn = vobcDA.create_dropdown_options()
        self.assertTrue(len(fn) == 16)

        fn0 = vobcDA.get_fault_name(-1)
        self.assertTrue(fn0 == '00. All')

    def test_sum_PD(self):
        df = vobcDA.get_count_by(-1, '2014-01-01T00:00:00', '2015-04-25T00:13:26.017995')
        pprint.pprint(df.groupby(['VOBCID']).sum().FaultCount.max())
        #y_max = df.groupby(['VOBCID'])['FaultCount'].sum().max()


    def test_str2date1(self):
        dt = util.str2date1('2010-1-1')
        self.assertTrue(isinstance(dt, datetime))

        dt = util.str2date1('2015-04-25T00:13:26.017995')
        self.assertTrue(isinstance(dt, datetime))
        self.assertTrue(dt.year == 2015)

    def test_trainmove(self):
        df = trainmoveDA.get_trainmove(248, '2015-01-03T10:51:30.160Z', '2015-01-13T11:51:30.160Z')
        self.assertTrue(len(df['loggedAt']) > 100)

    def test_get_first_fault_time(self):
        dt = vobcDA.get_first_fault_time('2015-07-03', 3, 78)
        self.assertTrue(dt.year == 2015)

if __name__ == '__main__':
    unittest.main()

# %%
