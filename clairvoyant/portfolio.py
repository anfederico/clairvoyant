from sklearn.svm import SVC
from sklearn.preprocessing import StandardScaler
from numpy import vstack, hstack
from csv import DictWriter
from dateutil.parser import parse
from pytz import timezone
from clairvoyant import Clair


class Portfolio(Clair):
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
        quote = getattr(row, attrs['Close'])
        return self.buyingPower+self.shares*quote

    def buyShares(self, shares, quote):
        if (shares*quote) <= self.buyingPower - self.transaction_cost:
            self.buyingPower -= shares*quote + self.transaction_cost
            self.shares += shares
            self.purchases += 1
        else:
            print("Sorry, insufficient buying power.")

    def sellShares(self, shares, quote):
        if shares <= self.shares:
            self.buyingPower += shares*quote - self.transaction_cost
            self.shares -= shares
            self.sales += 1
        else:
            print("Sorry, you don't own this many shares.")

    def buyLogic(self, confidence, row, attrs):
        quote = getattr(row, attrs['Close'])

        if confidence >= 0.9:
            shareOrder = int((self.buyingPower*0.7)/quote)
            self.buyShares(shareOrder, quote)
        elif confidence >= 0.8:
            shareOrder = int((self.buyingPower*0.5)/quote)
            self.buyShares(shareOrder, quote)
        elif confidence >= 0.75:
            shareOrder = int((self.buyingPower*0.3)/quote)
            self.buyShares(shareOrder, quote)

        if self.debug:
            super().buyLogic(confidence, row, attrs)
            print(f'Bought {shareOrder} @ ${quote}')

    def sellLogic(self, confidence, row, attrs):
        quote = getattr(row, attrs['Close'])
        if confidence >= 0.75 and self.shares > 0:
            if self.debug:
                super().sellLogic(confidence, row, attrs)
                print(f'Sold {self.shares} @ ${quote}')
            self.sellShares(self.shares, quote)

    def nextPeriodLogic(self, prediction, nextPeriodPerformance, row, attrs):
        if self.debug:
            super().nextPeriodLogic(
                prediction, nextPeriodPerformance, row, attrs
                )
        quote = getattr(row, attrs['Close'])

        if prediction == 1 and nextPeriodPerformance > 0:
            if nextPeriodPerformance >= 0.025:
                self.sellShares(self.shares, quote)
        elif prediction == -1 and nextPeriodPerformance <= 0:
            if nextPeriodPerformance <= -0.025:
                shareOrder = int((self.buyingPower*0.2)/quote)
                self.buyShares(shareOrder, quote)

        # Record Performance
        self.lastQuote = getattr(row, attrs['Close'])
        val = self.portfolioValue(row, attrs)
        self.performances.append(
            ((val-self.startingBalance)/self.startingBalance)*100
            )

    def displayLastRun(self):
        bld, gre, red, end = '\033[1m', '\033[92m', '\033[91m', '\033[0m'

        if self.runs < 1:
            print("Error: No last run"); return

        print(bld+"Run #"+str(self.runs)+end)
        print("Buying Power: $" + str(round(self.buyingPower,2)))
        print("Shares: " + str(self.shares))
        print(f'Buy Transactions: {self.purchases}')
        print(f'Sell Transactions: {self.sales}')

        totalValue = round(self.buyingPower+self.shares*self.lastQuote,2)
        if totalValue > self.startingBalance:
            val = round(self.buyingPower+self.shares*self.lastQuote,2)
            print(f'Total Value: ${gre}{val}{end}')
        elif totalValue < self.startingBalance:
            val = round(self.buyingPower+self.shares*self.lastQuote,2)
            print(f'Total Value: ${red}{val}{end}')
        else:
            val = round(self.buyingPower+self.shares*self.lastQuote,2)
            print(f'Total Value: ${val}')

    def displayAllRuns(self):
        bld, gre, red, end = '\033[1m', '\033[92m', '\033[91m', '\033[0m'

        print(f'{bld}Performance across all runs{end}')
        print(f'Runs: {self.runs}')

        try:
            averagePerformance = round(
                sum(self.performances)/len(self.performances),2
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
        self.startingBalance = 0
        self.buyingPower = 0
        self.shares = 0
        self.lastQuote = 0
        self.runs = 0
        self.performances = []
