

#%%
import unittest
import models.vobcfault_m as vobcDA
import pandas as pd
from datetime import datetime
from datetime import timedelta

#%%
'2020-04-25T00:13:26.017995'
'2015-01-01T00:00:00'

'2015-01-16'

class TestVOBC(unittest.TestCase):

    def test_get_count_by_fc(self):
        df_all = vobcDA.get_count_by_fc('00. All', '2015-01-01T00:00:00', '2020-04-25T00:13:26.017995')
        df_one = vobcDA.get_count_by_fc('03. FAR Level 3 Fault', '2015-01-01T00:00:00', '2020-04-25T00:13:26.017995')
        self.assertTrue( df_all['FaultCount'].count() > 0 )
        self.assertTrue( df_one['FaultCount'].count() > 0 )
        self.assertTrue( df_all['FaultCount'].count() > df_one['FaultCount'].count() )

    def test_get_count_by_fc_date(self):
        end  = datetime(2015,1,1)
        start = end - timedelta(days=100)
        df_all = vobcDA.get_count_by_fc('00. All', start, end)
        self.assertTrue( df_all['FaultCount'].count() > 0 )

    def test_get_count_by_date(self):
        df1 = vobcDA.get_count_by_fc('00. All', '2014-01-01T00:00:00', '2014-04-25T00:13:26.017995')
        df2 = vobcDA.get_count_by_fc('00. All', '2014-01-01T00:00:00', '2014-05-25T00:13:26.017995')
        self.assertTrue( df1['FaultCount'].count() > 0 )
        self.assertTrue( df2['FaultCount'].count() > 0 )
        self.assertTrue( df1['FaultCount'].count() < df2['FaultCount'].count() )

    def test_get_count_by_fc_one(self):
        df = vobcDA.get_count_by_fc('03. FAR Level 3 Fault', '2015-01-06', '2020-04-25T00:13:26.017995')
        self.assertTrue( df['FaultCount'].count() > 0 )


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
