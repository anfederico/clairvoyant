"""History manages historical stock timeseries data.

This module provides a common interface for ``Clair`` so that she knows how
your data is formatted. This requires you to define a column map for your data,
which maps your column names to common names that Clair understands.
"""

from pytz import timezone
import pandas as pd
from copy import deepcopy


class History:
    """A wrapper for historical stock data.

    Convenience features
    You can query for a row by date::

        history['2017-02-14 06:30:00']  # get data by a specific date

    You can slice using datetime objects or index numbers::

        history[startDate:endDate]  # get data between startDate and endDate
        history[0:100]              # get rows between 0 and 100

    You can get individual records by index::

        history[10]  # gets a row of data

    You can access a column of data by key just like a dataframe::

        history['Open']  # gets a column of data

    :param data: Client stock data. Can be a string representing a csv file or
                 it can be a pandas dataframe.
    :param col_map: A dict mapping your data's column names to common names
                    where the common names are keys and your custom names are
                    values. This is an optional parameter. If ``None`` is
                    provided, History will assume client data is already
                    formatted with common names.
    :param tz: The timezone to associate with the datetime in data. Default is
               UTC time.
    :param features: A list of column names that informs Clair which columns
                     can be used as learning features.

    :ivar date: Datetime series in data corresponding to the beginning of each
                period.
    :ivar open: Opening stock price series.
    :ivar high: Series of stock price highs.
    :ivar low: Series of stock price lows.
    :ivar close: Closing stock price series.
    :ivar volume: Series of stock price trading volume.
    :ivar return_rate: Series of percentage change calculated as a percent of
                       opening price.
    """

    def __init__(self, data, col_map=None, tz=timezone('UTC'), features=None):
        if col_map is None:
            self._col_map = {
                'Date': 'Date', 'Open': 'Open', 'High': 'High', 'Low': 'Low',
                'Close': 'Close', 'Volume': 'Volume', 'Sentiment': 'Sentiment',
                'Influence': 'Influence'
                }
        else:
            self._col_map = col_map

        if isinstance(data, str):
            self._df = self.read_csv(data)
        else:
            self._df = data

        # make sure all column names can be converted in itertuple
        newnames = {v: k.lower() for k, v in self._col_map.items()}
        self.rename(columns=newnames)

        if features is None:
            self.features = ['Sentiment', 'Influence']
        else:
            self.features = features

        self._timezone = tz
        self._df['Return'] = (self.close - self.open)/self.open
        self._col_map['Return'] = 'Return'

    @property
    def date(self):
        return self['Date']

    @property
    def open(self):
        return self['Open']

    @property
    def high(self):
        return self['High']

    @property
    def low(self):
        return self['Low']

    @property
    def close(self):
        return self['Close']

    @property
    def volume(self):
        return self['Volume']

    @property
    def return_rate(self):
        return self['Return']

    @property
    def features(self):
        return self._features

    @features.setter
    def features(self, vals):
        for v in vals:
            if v not in self._col_map.keys():
                raise KeyError(f'\'{v}\' is not a valid column.')
        self._features = vals

    def __deepcopy__(self, memo):
        cls = self.__class__
        result = cls.__new__(cls)
        memo[id(self)] = result
        for k, v in self.__dict__.items():
            setattr(result, k, deepcopy(v, memo))
        return result

    def __getitem__(self, key):
        if isinstance(key, slice):
            dc = deepcopy(self)
            if isinstance(key.start, int):
                dc._df = dc._df[key]
                return dc
            dc._df['dt'] = pd.to_datetime(dc._df[dc._col_map['Date']])
            try:
                dc._df['dt'].apply(dc._timezone.localize)
            except ValueError:
                pass
            mask = (dc._df['dt'] >= key.start) & (dc._df['dt'] <= key.stop)
            dc._df = dc._df[mask]
            dc._df = dc._df.drop('dt', 1)
            return dc
        elif isinstance(key, int):
            return self._df.iloc[key]

        try:
            return self._df[self._col_map[key]]
        except KeyError:
            try:
                pd.to_datetime(key)  # test conversion to datetime
                datekey = self._col_map['Date']
                return self._df.loc[self._df[datekey] == key]
            except ValueError:
                pass
            print(f'Invalid column map for {key}.')
            raise

    def __iter__(self):
        return self._df.itertuples()

    def __len__(self):
        return len(self._df)

    def read_csv(self, *args, **kwargs):
        """Read a csv file.

        Exact same interface as ``pandas.read_csv``.
        """
        return pd.read_csv(*args, **kwargs)

    def rename(self, *args, **kwargs):
        """Rename the stored dataframe columns.

        Exposes the exact same interface as ``pandas.DataFrame.rename``.
        """
        old_cols = {v: k for k, v in self._col_map.items()}
        for old_col, new_col in kwargs['columns'].items():
            try:
                self._col_map[old_cols[old_col]] = new_col
            except KeyError:
                continue

        self._df = self._df.rename(*args, **kwargs)
