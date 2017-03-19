from pytz import timezone
from pandas import to_datetime


class History:
    """
    Data wrapper.
    """
    def __init__(self, data, col_map=None, tz=timezone('UTC'), features=None):
        if col_map is None:
            self._col_map = {
                'Date': 'Date', 'Open': 'Open', 'High': 'High', 'Low': 'Low',
                'Close': 'Close', 'Volume': 'Volume', 'Sentiment': 'Sentiment',
                'Influence', 'Influence'
                }
        else:
            self._col_map = col_map

        if features = None:
            self._features = ['Sentiment', 'Influence']
        else:
            self._features = features

        if isinstance(data, str):
            self._df = self.read_csv(data)
        else:
            self._df = data

        self._timezone = tz

    @property
    def date(self):
        return self._df[self._col_map['Date']]

    def __iter__(self):
        pass

    def __getitem__(self):
        pass

    def read_csv(self, file):
        pass

    def read_sql(self, file):
        pass
