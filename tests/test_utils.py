import unittest
import clairvoyant as cvt
import pandas as pd
from pandas import to_datetime

class Test_Utils(unittest.TestCase):
    def setUp(self):
        dates = ['2017-01-01', '2017-01-02', '2017-01-03', '2017-01-03',
                 '2017-01-04', '2017-01-05', '2017-01-06']
        mock = [1, 2, 2, 1, 1, 1, 1]
        self.data = pd.DataFrame.from_dict(
            {'Date': [to_datetime(dt) for dt in dates],
             'mock': mock}
        )

    def test_date_index(self):
        date = to_datetime('2017-01-03')
        self.assertEqual(cvt.utils.DateIndex(self.data, date, True), 2)
        date = to_datetime('2017-01-06')
        self.assertEqual(cvt.utils.DateIndex(self.data, date, False), 6)
