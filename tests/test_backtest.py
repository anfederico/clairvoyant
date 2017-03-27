import unittest
from unittest.mock import patch, MagicMock
from clairvoyant import History, Backtest
import os
dir_path = os.path.dirname(os.path.realpath(__file__))


class Test_Backtest(unittest.TestCase):
    def setUp(self):
        column_map = {
            'Date': 'Unnamed: 0', 'Open': 'open', 'High': 'high', 'Low': 'low',
            'Close': 'close', 'Volume': 'volume', 'Sentiment': 'sentiment',
            'Influence': 'influence'
            }
        self.sample = History(
            os.path.join(dir_path, 'tsla-sentiment.csv'), col_map=column_map
            )
        self.variables = ['Sentiment', 'Influence']
        self.trainStart = '2017-02-23 06:30:00'
        self.trainEnd = '2017-03-09 12:30:00'
        self.testStart = '2017-03-10 06:30:00'
        self.testEnd = '2017-03-14 12:30:00'

        self.backtest = Backtest(
            self.variables, self.trainStart, self.trainEnd, self.testStart,
            self.testEnd
            )
        self.backtest.stocks = ['TSLA']

    def test_run(self):
        self.backtest.runModel(self.sample)
        self.assertTrue(True)
