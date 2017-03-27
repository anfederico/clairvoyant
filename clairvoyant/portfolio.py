"""Portfolio provides a basic portfolio class.

A portfolio defines a balance that is used in stock trading logic. In addition
to an implementation of trading strategy, it performs accounting functions to
keep track of the number of shares and running balance.

Clients may wish to subclass ``Portfolio`` to create variations based on the
aggressiveness of the trading logic or perhaps introduce additional trading
conditions. For example, different broker services may have different
transaction costs and pricing structures.

.. Todo:: This module is currently unfinished. Currently, portfolio can trade
   only one stock. It will be updated to allow multiple stock symbols.
"""

from pytz import timezone
from clairvoyant import Clair


class Portfolio(Clair):
    """Provides a basic portfolio framework for backtesting.

    :param variables: A list of columns that represent learning features.
    :param trainStart: A datetime as a string that should be consistent with
                       the ``tz`` parameter. Defines the start date for model
                       training.
    :param trainEnd: A datetime as a string that should be consistent with the
                     ``tz`` parameter. Defines the end date for model training.
    :param testStart: A datetime as a string that should be consistent with the
                      ``tz`` parameter. Defines the start date for model
                      testing.
    :param testEnd: A datetime as a string that should be consistent with the
                    ``tz`` parameter. Defines the end date for model testing.
    :param buyThreshold: Defines the confidence level at which Clair will
                         will recommend a buy. Default 0.65.
    :param sellThreshold: Defines the confidence level at which Clair will
                          recommend a sell. Default 0.65.
    :param C: A penalty parameter for false positives. See scikit-learn
              documentation for more details. Default 1.
    :param gamma: The kernel coefficient for machine learning. See scikit-learn
                  documentation for more details. Default 10.
    :param continuedTraining: Determine if data from the testing period should
                              be used to continue training the model during the
                              testing phase. Default False.
    :param tz: The timezone associated with the datetime parameters. Default
               UTC.
    :param transaction_cost: The amount deducted from balance after each trade.

    :ivar debug: A boolean value that determines if debug strings will be
                 printed as backtesting is run. Warning: may result in a lot of
                 output.
    :ivar startingBalance: The initial balance.
    :ivar buyingPower: Cash balance.
    :ivar shares: The number of shares of a stock.
    :ivar lastQuote: The latest available stock price.
    """

    def __init__(
            self, variables, trainStart, trainEnd, testStart, testEnd,
            buyThreshold=0.65, sellThreshold=0.65, C=1, gamma=10,
            continuedTraining=False, tz=timezone('UTC'), transaction_cost=9.99
            ):

        super().__init__(
            variables, trainStart, trainEnd, testStart, testEnd,
            buyThreshold=buyThreshold, sellThreshold=sellThreshold, C=C,
            gamma=gamma, continuedTraining=continuedTraining, tz=tz
            )

        # Conditions
        self.transaction_cost = transaction_cost

        # Run
        self.startingBalance = 0
        self.buyingPower = 0
        self.shares = 0
        self.lastQuote = 0
        self.debug = False

        # All runs
        self.runs = 0
        self.performances = []

    def runModel(self, data, startingBalance):
        """Backtest the porfolio strategy.

        :param data: Historical stock data.
        :param startingBalance: The beginning available cash balance.
        """
        self.runs += 1

        # Portfolio
        self.startingBalance = startingBalance
        self.buyingPower = startingBalance
        self.shares = 0
        self.lastQuote = 0
        self.purchases = 0
        self.sales = 0

        # Learn and execute
        model, X, y = self.learn(data)
        self.execute(data, model, X, y)

    def portfolioValue(self, row, attrs):
        """Determine the value of the portfolio.

        :param row: Stock data as a named tuple.
        :param attrs: A key map that maps common names to the named tuple keys.
        """
        quote = getattr(row, attrs['Close'])
        return self.buyingPower+self.shares*quote

    def buyShares(self, shares, quote):
        """Buy a certain number of shares.

        :param shares: The number of shares to buys.
        :param quote: The price to buy shares at.
        """
        if (shares*quote) <= self.buyingPower - self.transaction_cost:
            self.buyingPower -= shares*quote + self.transaction_cost
            self.shares += shares
            self.purchases += 1
        else:
            print("Sorry, insufficient buying power.")

    def sellShares(self, shares, quote):
        """Sell a certain number of shares.

        :param shares: The number of shares to sell.
        :param quote: The price to sell at.
        """
        if shares <= self.shares:
            self.buyingPower += shares*quote - self.transaction_cost
            self.shares -= shares
            self.sales += 1
        else:
            print("Sorry, you don't own this many shares.")

    def buyLogic(self, confidence, row, attrs):
        """Decide whether or not to buy shares."""
        quote = getattr(row, attrs['Close'])
        shareOrder = 0

        if confidence >= 0.9:
            shareOrder = int((self.buyingPower*0.7)/quote)
            self.buyShares(shareOrder, quote)
        elif confidence >= 0.8:
            shareOrder = int((self.buyingPower*0.5)/quote)
            self.buyShares(shareOrder, quote)
        elif confidence >= 0.75:
            shareOrder = int((self.buyingPower*0.3)/quote)
            self.buyShares(shareOrder, quote)

        if self.debug and shareOrder > 0:
            super().buyLogic(confidence, row, attrs)
            print(f'Bought {shareOrder} @ ${quote}')

    def sellLogic(self, confidence, row, attrs):
        """Decide whether or not to sell shares."""
        quote = getattr(row, attrs['Close'])
        if confidence >= 0.75 and self.shares > 0:
            if self.debug:
                super().sellLogic(confidence, row, attrs)
                print(f'Sold {self.shares} @ ${quote}')
            self.sellShares(self.shares, quote)

    def nextPeriodLogic(self, prediction, nextPeriodPerformance, row, attrs):
        """Record performance."""
        if self.debug:
            super().nextPeriodLogic(
                prediction, nextPeriodPerformance, row, attrs
                )

        if prediction == 1 and nextPeriodPerformance > 0:
            # An accurate prediction was made
            pass
        elif prediction == -1 and nextPeriodPerformance <= 0:
            # An accurate prediction was made
            pass

        # Record Performance
        self.lastQuote = getattr(row, attrs['Close'])
        val = self.portfolioValue(row, attrs)
        self.performances.append(
            ((val-self.startingBalance)/self.startingBalance)*100
            )

    def displayLastRun(self):
        """Print results of the latest run."""
        bld, gre, red, end = '\033[1m', '\033[92m', '\033[91m', '\033[0m'

        if self.runs < 1:
            print("Error: No last run")
            return

        print(bld+"Run #"+str(self.runs)+end)
        print("Buying Power: $" + str(round(self.buyingPower, 2)))
        print("Shares: " + str(self.shares))
        print(f'Buy Transactions: {self.purchases}')
        print(f'Sell Transactions: {self.sales}')

        totalValue = round(self.buyingPower+self.shares*self.lastQuote, 2)
        if totalValue > self.startingBalance:
            val = round(self.buyingPower+self.shares*self.lastQuote, 2)
            print(f'Total Value: ${gre}{val}{end}')
        elif totalValue < self.startingBalance:
            val = round(self.buyingPower+self.shares*self.lastQuote, 2)
            print(f'Total Value: ${red}{val}{end}')
        else:
            val = round(self.buyingPower+self.shares*self.lastQuote, 2)
            print(f'Total Value: ${val}')

    def displayAllRuns(self):
        """Print trading statistics."""
        bld, gre, red, end = '\033[1m', '\033[92m', '\033[91m', '\033[0m'

        print(f'{bld}Performance across all runs{end}')
        print(f'Runs: {self.runs}')

        try:
            averagePerformance = round(
                sum(self.performances)/len(self.performances), 2
                )
        except ZeroDivisionError:
            print("Average Performance: None\n")
            return

        if averagePerformance > 0:
            print(f'Average Performance: {gre}{averagePerformance}%{end}')
        elif averagePerformance < 0:
            print(f'Average Performance: {red}{averagePerformance}%{end}')
        else:
            print(f'Average Performance: {averagePerformance}%')

    def clearAllRuns(self):
        """Reset the portfolio."""
        self.startingBalance = 0
        self.buyingPower = 0
        self.shares = 0
        self.lastQuote = 0
        self.runs = 0
        self.performances = []
