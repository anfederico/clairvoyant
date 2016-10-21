<p align="center"><img src="https://github.com/anfederico/Clairvoyant/blob/master/media/Clairvoyant.png" width=60%></p>

[![PyPI version](https://badge.fury.io/py/clairvoyant.svg)](https://badge.fury.io/py/clairvoyant)
[![Build Status](https://travis-ci.org/anfederico/Clairvoyant.svg?branch=master)](https://travis-ci.org/anfederico/Clairvoyant)
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
from pandas import read_csv

# Testing performance on a single stock

variables  = ["SSO", "SSC"]     # Financial indicators of choice
trainStart = '2013-03-01'       # Start of training period
trainEnd   = '2015-07-15'       # End of training period
testStart  = '2015-07-16'       # Start of testing period
testEnd    = '2016-09-17'       # End of training period
buyThreshold  = 0.65            # Confidence threshold for predicting buy (default = 0.65) 
sellThreshold = 0.65            # Confidence threshold for predicting sell (default = 0.65)

backtest = Backtest(variables, '2013-03-01', '2015-07-15', '2015-07-16', '2016-09-17', continuedTraining = False)

data = read_csv("Stocks/SBUX.csv")      # Read in data
data = data.round(3)                    # Round all values                  
backtest.stocks.append("SBUX")          # Inform the model which stock is being tested
for i in range(0,10):                   # Run the model 10-15 times  
    backtest.runModel(data)

backtest.displayConditions()
backtest.displayStats()
    
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
        backtest.runModel(data)
        
backtest.displayConditions()
backtest.displayStats()
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


#### Visualize Model
```python
backtest.visualizeModel()
```

#### Portfolio Simulation

```python


```

## Other Features

#### Multivariate Functionality
```python
variables = ["SSO"]                            # 1 feature
variables = ["SSO", "SSC"]                     # 2 features
variables = ["SSO", "SSC", "RSI"]              # 3 features
variables = ["SSO", "SSC", "RSI", ... , Xn]    # n features

```

#### User Defined Trading Logic
```python

```

#### Continue Training
```python
continuedTraining = False:    # Don't Update model during testing period
continuedTraining = True:     # Update model during testing period (runtime increase)
```

#### Modify learning parameters
```python
C = 1:                        # Penalty parameter C of the error term.
gamma = 10:                   # Kernel coefficient for radial basis function
```

