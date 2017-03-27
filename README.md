<p align="center"><img width=15% src="https://cdn.rawgit.com/uclatommy/Clairvoyant/617dc9fb/media/logo.svg"></p>
<p align="center"><img width=60% src="https://github.com/uclatommy/Clairvoyant/blob/master/media/Clairvoyant.png"></p>

<p align="center">
<a href="https://travis-ci.org/uclatommy/Clairvoyant">
    <image src="https://travis-ci.org/uclatommy/Clairvoyant.svg?branch=master">
</a>
<a href="https://github.com/uclatommy/Clairvoyant/issues">
     <img src="https://img.shields.io/github/issues/uclatommy/Clairvoyant.svg">
</a>
<a href="https://www.python.org/">
     <img src="https://img.shields.io/badge/python-3.6%2B-blue.svg">
</a>
<a href="https://uclatommy.github.io/Clairvoyant/">
    <img src="https://img.shields.io/badge/docs-0.2.0-blue.svg?style=flat">
</a>
<a href="https://opensource.org/licenses/MIT">
     <img src="https://img.shields.io/badge/license-MIT%20License-brightgreen.svg">
</a>
</p>

## Basic Overview

Using stock historical data, train a supervised learning algorithm with any combination of financial indicators. Rapidly backtest your model for accuracy and simulate investment portfolio performance.
<p align="center"><img width=95% src="https://github.com/anfederico/Waldo/blob/master/media/Schematic.png"></p>

<br>

## Visualize the Learning Process
<img src="https://github.com/anfederico/Clairvoyant/blob/master/media/Learning.gif" width=40%>

<br>

## Install
```python
pip3 install clairvoyant
```

<br>

## Code Examples

#### Backtesting Signal Accuracy
During the testing period, the model signals to buy or sell based on its prediction for price
movement the following day. By putting your trading algorithm aside and testing for signal accuracy
alone, you can rapidly build and test more reliable models.

```python
from clairvoyant import Backtest, History

# Testing performance on a single stock

variables  = ["SSO", "SSC"]     # Financial indicators of choice
trainStart = '2013-03-01'       # Start of training period
trainEnd   = '2015-07-15'       # End of training period
testStart  = '2015-07-16'       # Start of testing period
testEnd    = '2016-07-16'       # End of testing period
buyThreshold  = 0.65            # Confidence threshold for predicting buy (default = 0.65)
sellThreshold = 0.65            # Confidence threshold for predicting sell (default = 0.65)
C = 1                           # Penalty parameter (default = 1)
gamma = 10                      # Kernel coefficient (default = 10)
continuedTraining = False       # Continue training during testing period? (default = false)

backtest = Backtest(variables, trainStart, trainEnd, testStart, testEnd)

cols = {'Date': 'date', 'Open': 'open', 'Close': 'close',
        'SSO': 'sentiment', 'SSC': 'influence'}       # Define a column map
data = History("Stocks/SBUX.csv", col_map=cols)       # Read in data       
backtest.stocks.append("SBUX")                        # Inform the model which stock is being tested
for i in range(0,10):                                 # Run the model 10-15 times  
    backtest.runModel(data)

# Testing performance across multiple stocks

stocks = ["AAPL", "ADBE", "AMGN", "AMZN",
          "BIIB", "EBAY", "GILD", "GRPN",
          "INTC", "JBLU", "MSFT", "NFLX",
          "SBUX", "TSLA", "VRTX", "YHOO"]

for stock in stocks:
    data = History(f'Stocks/{stock}.csv', col_map=cols)
    backtest.stocks.append(stock)
    for i in range(0,10):
        backtest.runModel(data)

backtest.displayConditions()
backtest.displayStats()        
```

#### View Results

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

#### Portfolio Simulation
Once you've established your model can accurately predict price movement a day in advance,
simulate a portfolio and test your performance with a particular stock. User defined trading logic
lets you control the flow of your capital based on the model's confidence in its prediction
and the following next day outcome.

```python
from clairvoyant import Portfolio, History

variables  = ["SSO", "SSC", "SSL"]   # Financial indicators of choice
trainStart = '2013-03-01'            # Start of training period
trainEnd   = '2015-07-15'            # End of training period
testStart  = '2015-07-16'            # Start of testing period
testEnd    = '2016-07-16'            # End of testing period
buyThreshold  = 0.65                 # Confidence threshold for predicting buy (default = 0.65)
sellThreshold = 0.65                 # Confidence threshold for predicting sell (default = 0.65)
C = 1                                # Penalty parameter (default = 1)
gamma = 10                           # Kernel coefficient (default = 10)
continuedTraining = False            # Continue training during testing period? (default = false)
startingBalance = 1000000            # Starting balance of portfolio

# User defined trading logic (see below)
class MyStrategy(Portfolio):
    def buyLogic(self, confidence, row, colmap):
      ...
    def sellLogic(self, confidence, row, colmap):
      ...
    def nextPeriodLogic(self, prediction, nextDayPerformance, row, colmap):
      ...

portfolio = MyStrategy(variables, trainStart, trainEnd, testStart, testEnd)

data = History("Stocks/YHOO.csv", col_map=cols)
for i in range(0,5):
    portfolio.runModel(data, startingBalance)
    portfolio.displayLastRun()

portfolio.displayAllRuns()
```

#### View Results
<pre>
<b>Run #1</b>
Buying Power: $664488.82
Shares: 10682
Total Value: $<strong style="color: green;">1130971.76</strong>
<b>Run #2</b>
Buying Power: $588062.6
Shares: 10654
Total Value: $<strong style="color: green;">1053322.78</strong>
<b>Run #3</b>
Buying Power: $787542.42
Shares: 7735
Total Value: $<strong style="color: green;">1125329.87</strong>
<b>Run #4</b>
Buying Power: $783145.32
Shares: 7692
Total Value: $<strong style="color: green;">1119054.96</strong>
<b>Run #5</b>
Buying Power: $648025.83
Shares: 10418
Total Value: $<strong style="color: green;">1102979.9</strong>
<br>
<b>Performance across all runs</b>
Runs: 5
Average Performance: <strong style="color: green;">10.63%</strong>
</pre>

<br>

## Examples continued...

#### Visualize Model
This feature will give you an immediate sense of how predictable your data is.
```python
backtest.visualizeModel()
```
<img src="https://cdn.rawgit.com/uclatommy/Clairvoyant/f771124f/media/TSLA.svg" width=50%>

#### User Defined Trading Logic
These functions will tell your portfolio simulation how to trade. We tried to balance simplicity and
functionality to allow for intricate trading strategies.
```python
class MyStrategy(Portfolio):
    def buyLogic(self, confidence, row, colmap):
        quote = getattr(row, colmap['Close'])                    # Leave as is

        if confidence >= 0.75:                                   # If model signals buy
            shareOrder = int((self.buyingPower*0.3)/quote)       # and is 75-100% confident
            self.buyShares(shareOrder, quote)                    # invest 30% of buying power    

        elif confidence >= 0.70:                                 # If model is 70-75% confident
            shareOrder = int((self.buyingPower*0.2)/quote)       # invest 20% of buying power
            self.buyShares(shareOrder, quote)

        elif confidence >= 0.65:                                 # If model is 65-70% confident
            shareOrder = int((self.buyingPower*0.1)/quote)       # invest 10% of buying power
            self.buyShares(shareOrder, quote)


    def sellLogic(self, confidence, row, colmap):
        quote = getattr(row, colmap['Close'])                       

        if confidence >= 0.65:                                   # If model signals sell
            self.sellShares(self.shares, quote)                  # and is 65-100% confident
                                                                 # sell all shares    

    def nextDayLogic(self, prediction, nextPeriodPerformance, row, colmap):
        quote = getattr(row, colmap['Close'])                        

        # Case 1: Prediction is buy, price increases
        if prediction == 1 and nextPeriodPerformance > 0:

            if nextPeriodPerformance >= 0.025:                   # If I bought shares
                self.sellShares(self.shares, quote)              # and price increases >= 2.5%
                                                                 # sell all shares

        # Case 2: Prediction is buy, price decreases
        elif prediction == 1 and nextPeriodPerformance <= 0: pass

                                                                 # If I bought shares
                                                                 # and price decreases
                                                                 # hold position

        # Case 3: Prediction is sell, price decreases
        elif prediction == -1 and nextPeriodPerformance <= 0:

            if nextPeriodPerformance <= -0.025:                  # If I sold shares
                shareOrder = int((self.buyingPower*0.2)/quote)   # and price decreases >= 2.5%
                self.buyShares(shareOrder, quote)                # reinvest 20% of buying power

        # Case 4: Prediction is sell, price increases
        elif prediction == -1 and nextPeriodPerformance > 0: pass

                                                                 # If I sold shares
                                                                 # and price increases
                                                                 # hold position
        # Case 5: No confident prediction was made
```

#### Multivariate Functionality
Remember, more is not always better!
```python
variables = ["SSO"]                            # 1 feature
variables = ["SSO", "SSC"]                     # 2 features
variables = ["SSO", "SSC", "RSI"]              # 3 features
variables = ["SSO", "SSC", "RSI", ... , Xn]    # n features
```

#### Flexible Data Handling
Download historical data directly from popular distribution sources. Clairvoyant is
flexible with most date formats and will ignore unused columns in the dataset. If it
can't find the date specified, it will choose a suitable alternative.
```text
Date,Open,High,Low,Close,Volume,influence,sentiment
03/01/2013,27.72,27.98,27.52,27.95,34851872,65.7894736842,-0.121
03/04/2013,27.85,28.15,27.7,28.15,38167504,75.9450171821,0.832
03/05/2013,28.29,28.54,28.16,28.35,41437136,84.9230769231,0.151
03/06/2013,28.21,28.23,27.78,28.09,51448912,80.7799442897,-0.689
03/07/2013,28.11,28.28,28.005,28.14,29197632,73.5368956743,-0.821
```
#### Social Sentiment Scores
The examples shown use data derived from a project where we are data mining
social media and performing stock sentiment analysis.
```
https://github.com/uclatommy/TweetFeels
```
