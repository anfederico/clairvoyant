import unittest
import pandas as pd
import os
from clairvoyant import History
dir_path = os.path.dirname(os.path.realpath(__file__))


class Test_History(unittest.TestCase):
    def setUp(self):
        self.sample = History(os.path.join(dir_path,'tsla-sentiment.csv'))

    def test_get_data(self):
        data = self.sample
        self.assertTrue(isinstance(data._df, pd.DataFrame))
        self.assertRaises(KeyError, data.__getitem__, 'Date')
        self.sample._col_map['Close'] = 'close'
        # You can get a column by name, returns a series.
        self.assertTrue(isinstance(data['Close'], pd.Series))
        # You can get a column by attribute, returns a series.
        self.assertTrue(isinstance(data.close, pd.Series))

    def test_rename(self):
        data = self.sample
        data.rename(columns={'Unnamed: 0': 'Date', 'Close': 'close'})
        self.assertEqual(data._col_map['Date'], 'Date')
        self.assertEqual(data._col_map['Close'], 'close')
        self.assertTrue(isinstance(data.date, pd.Series))
        self.assertTrue(isinstance(data.close, pd.Series))

    def test_iteration(self):
        data = self.sample
        count = 0
        for i in data:
            count += 1
        print(count)
        self.assertEqual(count, 232)

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
        data.rename(columns={'Unnamed: 0': 'Date'})

        print(data[-1])
        # You can get by index, returns a series
        self.assertTrue(isinstance(data[0], pd.Series))
        self.assertEqual(data[-1]['Date'], '2017-03-10 13:00:00')

        print(data['2017-03-10 13:00:00'])
        # You can also get by date, returns a dataframe
        self.assertTrue(isinstance(data['2017-03-10 13:00:00'], pd.DataFrame))
        self.assertEqual(data['2017-03-10 13:00:00'].index[0], 231)
