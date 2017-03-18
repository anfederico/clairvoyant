import unittest
import clairvoyant as cvt
import pandas as pd
from pandas import to_datetime

class Test_Utils(unittest.TestCase):
    def setUp(self):
        dates = ['2017-01-01', '2017-01-02', '2017-01-03', '2017-01-03',
                 '2017-01-04', '2017-01-05', '2017-01-06']
        SSO = [0.5, 0.4, 0.2, -0.5, -0.4, -0.9, 0.9]
        SSC = [100, 200, 200, 100, 123, 456, 789]
        c = [100, 101, 103, 99, 101, 98, 100]
        o = [99, 100, 100.5, 103, 99, 101, 98]
        self.data = pd.DataFrame.from_dict(
            {'Date': [to_datetime(dt) for dt in dates],
             'SSO': SSO, 'SSC': SSC, 'Open': o, 'Close': c }
        )
        self.data2 = pd.read_csv('tests/tsla-sentiment.csv')
        self.data2 = self.data2.rename(columns={'Unnamed: 0': 'Date'})
        self.data2.Date = to_datetime(self.data2.Date)

    def test_date_index(self):
        date = to_datetime('2017-01-03')
        self.assertEqual(cvt.utils.DateIndex(self.data, date, True), 2)
        date = to_datetime('2017-01-06')
        self.assertEqual(cvt.utils.DateIndex(self.data, date, False), 6)
        date = to_datetime('2017-02-23 06:45:00')
        self.assertEqual(cvt.utils.DateIndex(self.data2, date, True), 1)


    def test_find_conditions(self):
        print(self.data.head())
        day = cvt.utils.DateIndex(self.data, to_datetime('2017-01-02'), False)
        ssc = cvt.utils.FindConditions(self.data, day, 'SSC')
        self.assertEqual(ssc, 200)
        day = cvt.utils.DateIndex(self.data, to_datetime('2017-01-06'), False)
        sso = cvt.utils.FindConditions(self.data, day, 'SSO')
        self.assertEqual(sso, 0.9)


    def test_percent_change(self):
        day = cvt.utils.DateIndex(self.data, to_datetime('2017-01-02'), False)
        delta = cvt.utils.PercentChange(self.data, day)
        self.assertEqual(delta, 0.01)
