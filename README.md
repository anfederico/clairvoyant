# Clairvoyant

[![Packagist](https://img.shields.io/packagist/l/doctrine/orm.svg)]()

## Basic Overview

#### Schematic
Using stock historical data, train a supervised learning algorithm with any combination of financial indicators. Rapidly backtest your model for accuracy and simulate investment portfolio performance. 
<p align="center"><img src="https://github.com/anfederico/Waldo/blob/master/media/Schematic.png" width=100%></p>

#### Visualize the Learning Process
<img src="https://github.com/anfederico/Waldo/blob/master/media/TSLA.gif" width=50%><

## Install
```python
pip install clairvoyant
```
## Code Examples

#### Backtesting Signal Accuracy
During the testing period, the model signals to buy or sell based on its prediction for price
movement the following day. By putting your trading algorithm aside and testing for signal accuracy
alone, you can rapidly build and test more reliable models.

```python
from clairvoyant import Backtest

# Testing performance on a single stock

variables  = ["SSO", "SSC"]     # Financial indicators of choice
trainStart = '2013-03-01'       # Start of training period
trainEnd   = '2015-07-15'       # End of training period
testStart  = '2015-07-16'       # Start of testing period
testEnd    = '2016-09-17'       # End of training period
buyThreshold  = 0.65            # Confidence threshold for predicting buy (default = 0.65) 
sellThreshold = 0.65            # Confidence threshold for predicting sell (default = 0.65)

backtest = Backtest(variables, trainStart, trainEnd, testStart, testEnd, buyThreshold, sellThreshold)

data = read_csv("Stocks/SBUX.csv")      # Read in data
data = data.round(3)                    # Round all values                  
backtest.stocks.append("SBUX")          # Inform the model which stock is being tested
for i in range(0,10):                   # Run the model 10-15 times  
    testSession.runModel(data)

# Testing performance across multiple stocks

stocks = ["AAPL", "ADBE", "AMGN", "AMZN",
          "BIIB", "EBAY", "GILD", "GRPN", 
          "INTC", "JBLU", "MSFT", "NFLX", 
          "SBUX", "TSLA", "VRTX", "YHOO"]

for stock in stocks:
    data = read_csv('Stocks/%s.csv' % stock)
    data = data.round(3)
    backtest.stocks.append(stock)
    for i in range(0,10):
        testSession.runModel(data)
```

#### View Results
```python
backtest.displayConditions()
backtest.displayStats()
```
<pre>
<b>Conditions</b>
X1: SSO
X2: SSC
Buy Threshold: 65.0%
Sell Threshold: 65.0%
C: 1
gamma: 10
Continued Training: False
<br>
<b>Stats</b>
Stock(s):
AAPL | Training: 03/01/2013-07/15/2015 Testing: 07/16/2015-07/15/2016
ADBE | Training: 03/01/2013-07/15/2015 Testing: 07/16/2015-07/15/2016
AMGN | Training: 03/01/2013-07/15/2015 Testing: 07/16/2015-07/15/2016
AMZN | Training: 03/01/2013-07/15/2015 Testing: 07/16/2015-07/15/2016
BIIB | Training: 03/01/2013-07/15/2015 Testing: 07/16/2015-07/15/2016
EBAY | Training: 03/01/2013-07/15/2015 Testing: 07/16/2015-07/15/2016
GILD | Training: 03/01/2013-07/15/2015 Testing: 07/16/2015-07/15/2016
GRPN | Training: 03/01/2013-07/15/2015 Testing: 07/16/2015-07/15/2016
INTC | Training: 03/01/2013-07/15/2015 Testing: 07/16/2015-07/15/2016
JBLU | Training: 03/01/2013-07/15/2015 Testing: 07/16/2015-07/15/2016
MSFT | Training: 03/01/2013-07/15/2015 Testing: 07/16/2015-07/15/2016
NFLX | Training: 03/01/2013-07/15/2015 Testing: 07/16/2015-07/15/2016
SBUX | Training: 03/01/2013-07/15/2015 Testing: 07/16/2015-07/15/2016
TSLA | Training: 03/01/2013-07/15/2015 Testing: 07/16/2015-07/15/2016
VRTX | Training: 03/01/2013-07/15/2015 Testing: 07/16/2015-07/15/2016
YHOO | Training: 03/01/2013-07/15/2015 Testing: 07/16/2015-07/15/2016
<br>
Total Buys: 39
Buy Accuracy: <strong style="color: green;">62.86%</strong>
Total Sells: 20
Sell Accuracy: <strong style="color: green;">70.41%</strong>
</pre>

#### Multivariate Functionality
```python
variables = ["SSO"]                            # 1 Feature
variables = ["SSO", "SSC"]                     # 2 Features
variables = ["SSO", "SSC", "RSI"]              # 3 Features
variables = ["SSO", "SSC", "RSI", ... , Xn]    # n Features

```

#### Visualize Model
```python
backtest.visualizeModel()
```


#### Portfolio Simulations

```python


```
