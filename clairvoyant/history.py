from pytz import timezone
import pandas as pd


class History:
    """
    Data wrapper.
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

        if features is None:
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
    def features(self):
        return self._features

    @features.setter
    def features(self, vals):
        for v in vals:
            if v not in self._col_map.keys():
                raise KeyError(f'\'{v}\' is not a valid column.')
        self._features = vals

    def __getitem__(self, key):
        if isinstance(key, int):
            return self._df.iloc[key]
        try:
            return self._df[self._col_map[key]]
        except KeyError:
            try:
                datekey = self._col_map['Date']
                return self._df.loc[self._df[datekey]==key]
            except ValueError:
                pass
            print(f'Invalid column map for {key}.')
            raise

    def __iter__(self):
        return self._df.iterrows()

    def __len__(self):
        return len(self._df)

    def read_csv(self, *args, **kwargs):
        """
        Exact same interface as ``pandas.read_csv``.
        """
        return pd.read_csv(*args, **kwargs)

    def rename(self, *args, **kwargs):
        """
        Renames the stored dataframe columns. Exposes the exact same interface
        as ``pandas.DataFrame.rename``.
        """
        old_cols = {v:k for k,v in self._col_map.items()}
        for old_col, new_col in kwargs['columns'].items():
            try:
                self._col_map[old_cols[old_col]] = new_col
            except KeyError:
                continue

        self._df = self._df.rename(*args, **kwargs)


    def read_sql(self, *args, **kwargs):
        """
        Exact same interface as ``pandas.read_sql``.
        """
        return pd.read_sql(*args, **kwargs)
