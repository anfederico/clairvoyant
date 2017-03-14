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

    def test_date_index(self):
        date = to_datetime('2017-01-03')
        self.assertEqual(cvt.utils.DateIndex(self.data, date, True), 2)
        date = to_datetime('2017-01-06')
        self.assertEqual(cvt.utils.DateIndex(self.data, date, False), 6)

    def test_find_conditions(self):
        self.data.set_index('Date', inplace=True)
        ssc = cvt.utils.FindConditions(
            self.data, to_datetime('2017-01-02'), 'SSC'
        )
        self.assertEqual(ssc, 200)
        sso = cvt.utils.FindConditions(
            self.data, to_datetime('2017-01-06'), 'SSO'
        )
        self.assertEqual(sso, 0.9)

    def test_percent_change(self):
        self.data.set_index('Date', inplace=True)
        delta = cvt.utils.PercentChange(self.data, to_datetime('2017-01-02'))
        self.assertEqual(delta, 0.01)
