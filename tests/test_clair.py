import unittest
from unittest.mock import patch, MagicMock


class Test_Clair(unittest.TestCase):
    def setUp(self):
        self.variables  = ["sentiment", "influence"]
        self.trainStart = '2017-02-23 06:30:00'
        self.trainEnd   = '2017-03-09 12:30:00'
        self.testStart  = '2017-03-10 06:30:00'
        self.testEnd    = '2017-03-14 12:30:00'
