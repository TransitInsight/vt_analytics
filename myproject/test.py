#%%
import unittest
import models.vobcfault_m as vobcDA
import pandas as pd

'2020-04-25T00:13:26.017995'
'2015-01-01T00:00:00'

'2015-01-16'

class TestVOBC(unittest.TestCase):

    def test_get_count_by_fc_all(self):
        df = vobcDA.get_count_by_fc('00. All', '2015-01-01T00:00:00', '2020-04-25T00:13:26.017995')
        self.assertEqual('foo'.upper(), 'FOO')

    def test_get_count_by_fc_one(self):
        df = vobcDA.get_count_by_fc('03. FAR Level 3 Fault', '2015-01-06', '2020-04-25T00:13:26.017995')
        self.assertEqual('foo'.upper(), 'FOO')


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
