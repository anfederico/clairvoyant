def DateIndex(data, date, end, stock=None):
    lowbound = data["Date"][0]
    uppbound = data["Date"][len(data)-1]
    while (date >= lowbound and date <= uppbound):
        try:
            return data.Date[data.Date == date].index[0]
        except:
            if not end:
                date += relativedelta(days=1)
            else:
                date -= relativedelta(days=1)
    if stock is not None:
        stock = " in " + stock
    else:
        stock = ""
    raise ValueError("Couldn't find "+date.strftime('%m/%d/%Y')+" or suitable alternative"+stock)

def FindConditions(data, day, indicator):
    return data[indicator][day]

def PercentChange(data, day):
    return (data["Close"][day] - data["Open"][day]) / data["Open"][day]

def Predict(model, Xs):
    prediction = model.predict_proba([Xs])[0]
    negative = prediction[0]
    positive = prediction[1]
    return negative, positive
