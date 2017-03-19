from pandas.tslib import relativedelta

def DateIndex(data, date, end, stock=None):
    lowbound = data["Date"][0]
    uppbound = data["Date"][len(data)-1]
    while (date >= lowbound and date <= uppbound):
        try:
            return data.Date[data.Date == date].index[0]
        except:
            if not end:
                date += relativedelta(minutes=1)
            else:
                date -= relativedelta(minutes=1)
    if stock is not None:
        stock = " in " + stock
    else:
        stock = ""
    raise ValueError("Couldn't find "+date.strftime('%m/%d/%Y %H:%M:%S')+" or suitable alternative"+stock)

def FindConditions(data, period, indicator):
    return data[indicator][period]

def PercentChange(data, period):
    return (data["Close"][period] - data["Open"][period]) / data["Open"][period]
