import unittest
import numpy as np
import pandas as pd
import os
import pytz
from clairvoyant import History
dir_path = os.path.dirname(os.path.realpath(__file__))


class Test_History(unittest.TestCase):
    def setUp(self):
        column_map = {
            'Date': 'Unnamed: 0', 'Open': 'open', 'High': 'high', 'Low': 'low',
            'Close': 'close', 'Volume': 'volume', 'Sentiment': 'sentiment',
            'Influence': 'influence'
            }
        self.sample = History(
            os.path.join(dir_path, 'tsla-sentiment.csv'), col_map=column_map
            )

    def test_get_data(self):
        data = self.sample
        self.assertTrue(isinstance(data._df, pd.DataFrame))
        # KeyError happens if the column doesn't exist.
        self.assertRaises(KeyError, data.__getitem__, 'Blah')
        # You can get a column by name, returns a series.
        self.assertTrue(isinstance(data['Close'], pd.Series))
        # You can get a column by attribute, returns a series.
        self.assertTrue(isinstance(data.close, pd.Series))

    def test_rename(self):
        data = self.sample
        data.rename(columns={'date': 'Date', 'close': 'Close'})
        self.assertEqual(data._col_map['Date'], 'Date')
        self.assertEqual(data._col_map['Close'], 'Close')
        self.assertTrue(isinstance(data.date, pd.Series))
        self.assertTrue(isinstance(data.close, pd.Series))

    def test_iteration(self):
        data = self.sample
        count = 0
        for i in data:
            count += 1
        print(count)
        self.assertEqual(count, 232)

    def test_slicing_with_dates(self):
        data = self.sample
        tz = data._timezone
        start = tz.localize(pd.to_datetime('2017-02-24 06:30:00'))
        end = tz.localize(pd.to_datetime('2017-02-24 07:00:00'))
        # slicing produces a new History object
        cpy = data[start:end]
        self.assertEqual(cpy.date.iloc[0], '2017-02-24 06:30:00')
        self.assertEqual(cpy.date.iloc[-1], '2017-02-24 07:00:00')
        # renaming will change the namedtuple attributes
        data.rename(columns={'date': 'mydate'})
        for row in data[start:end]:
            self.assertTrue(hasattr(row, 'mydate'))
            self.assertFalse(hasattr(row, 'date'))

    def test_slicing_with_integers(self):
        data = self.sample
        # can also slice by integer index
        for row in data[0:3]:
            self.assertTrue(isinstance(row, tuple))
            self.assertTrue(hasattr(row, 'date'))

    def test_len(self):
        data = self.sample
        self.assertEqual(len(data), 232)

    def test_features(self):
        data = self.sample
        self.assertEqual(data.features, ['Sentiment', 'Influence'])
        data.features = ['Volume']
        self.assertEqual(data.features, ['Volume'])
        self.assertRaises(KeyError, setattr, data, 'features', ['test'])

    def test_getting_rows(self):
        data = self.sample

        print(data[-1])
        # You can get by index, returns a series
        self.assertTrue(isinstance(data[0], pd.Series))
        self.assertEqual(data.date.iloc[-1], '2017-03-10 13:00:00')

        print(data['2017-03-10 13:00:00'])
        # You can also get by date, returns a dataframe
        self.assertTrue(isinstance(data['2017-03-10 13:00:00'], pd.DataFrame))
        self.assertEqual(data['2017-03-10 13:00:00'].index[0], 231)

    def test_rate_of_return(self):
        data = self.sample
        self.assertTrue(np.isclose(
            data.return_rate[1], -0.00061491160645644951)
            )
