"""Backtest provides a way of exploring and testing various parameterizations.

This module provides classes that allow clients to experiment with different
machine learning parameterizations and test those on historical stock data.
"""
from numpy import meshgrid, arange, c_
from sklearn.preprocessing import StandardScaler
from numpy import vstack, hstack
from pytz import timezone
from clairvoyant import Clair
import matplotlib
matplotlib.use('Agg')


class Backtest(Clair):
    """Backtest is a type of machine learning classifier.

    The purpose of ``Backtest`` is to collect statistics on the performance of
    learned classifications while providing a quick and easy way to vary
    parameters for rapid experimentation. Backtest also provides some
    convenience functions for visualizing collected statistics.

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

    :ivar debug: A boolean value that determines if debug strings will be
                 printed as backtesting is run. Warning: may result in a lot of
                 output.
    """

    def __init__(
            self, variables, trainStart, trainEnd, testStart, testEnd,
            buyThreshold=0.65, sellThreshold=0.65, C=1, gamma=10,
            continuedTraining=False, tz=timezone('UTC')
            ):

        super().__init__(
            variables, trainStart, trainEnd, testStart, testEnd,
            buyThreshold=buyThreshold, sellThreshold=sellThreshold, C=C,
            gamma=gamma, continuedTraining=continuedTraining, tz=tz
            )

        # Stats
        self.stocks = []
        self.dates = []
        self.totalBuys = 0
        self.correctBuys = 0
        self.totalSells = 0
        self.correctSells = 0
        self.increases = 0
        self.decreases = 0
        self.periods = 0

        self.debug = False

        # Visualize
        self.XX = None
        self.yy = None
        self.model = None

    def runModel(self, data):
        """Run backtesting.

        :param data: A ``History`` of stock data that includes observations in
                     both the training and test phases.
        """
        # Learn and execute
        model, X, y = self.learn(data)
        self.execute(data, model, X, y)

        # Save for vizualization purposes
        self.dates.append([
            self.trainStart.strftime('%m/%d/%Y'),
            self.trainEnd.strftime('%m/%d/%Y'),
            self.testStart.strftime('%m/%d/%Y'),
            self.testEnd.strftime('%m/%d/%Y')
            ])

        XX = vstack(X)
        yy = hstack(y)
        self.XX = XX
        self.yy = yy
        self.model = model

    def buyLogic(self, *args, **kwargs):
        """Increment the buy count."""
        self.totalBuys += 1
        if self.debug:
            super().buyLogic(*args, **kwargs)

    def sellLogic(self, *args, **kwargs):
        """Increment the sell count."""
        self.totalSells += 1
        if self.debug:
            super().sellLogic(*args, **kwargs)

    def nextPeriodLogic(self, prediction, performance, *args, **kwargs):
        """Collect statistics on correct and incorrect buys and sells.

        :param prediction: Value of 1 or -1 representing an up or down
                           performance.
        :param performance: A positive or negative value representing the
                            actual observed performance.
        """
        self.periods += 1
        if performance > 0:
            self.increases += 1
            if prediction == 1:
                self.correctBuys += 1
        elif performance < 0:
            self.decreases += 1
            if prediction == -1:
                self.correctSells += 1

        if self.debug:
            super().nextPeriodLogic(prediction, performance, *args, **kwargs)

    def clearStats(self):
        """Reset all collected statistics."""
        self.dates = []
        self.totalBuys = 0
        self.correctBuys = 0
        self.totalSells = 0
        self.correctSells = 0
        self.increases = 0
        self.decreases = 0
        self.periods = 0

    def buyStats(self):
        """Return the collected buy statistics."""
        try:
            return round((float(self.correctBuys)/self.totalBuys)*100, 2)
        except ZeroDivisionError:
            return float(0)

    def sellStats(self):
        """Return the collected sell statistics."""
        try:
            return round((float(self.correctSells)/self.totalSells)*100, 2)
        except ZeroDivisionError:
            return float(0)

    def displayConditions(self):
        """Print the learning and testing parameters."""
        bld, end = '\033[1m', '\033[0m'

        print(f'{bld}Conditions{end}')
        i = 1
        for var in self.variables:
            print(f"X{i}: {var}")
            i += 1

        print(f"Buy Threshold: {self.buyThreshold*100}%")
        print(f"Sell Threshold: {self.sellThreshold*100}%")
        print(f"C: {self.C}")
        print(f"gamma: {self.gamma}")
        print(f"Continued Training: {self.continuedTraining}")
        print(f"Total Testing Periods: {self.periods}")
        print(f"Total Price Increases: {self.increases}")
        print(f"Total Price Decreases: {self.decreases}")

    def displayStats(self):
        """Print the collected backtesting statistics."""
        bld, gre, red, end = '\033[1m', '\033[92m', '\033[91m', '\033[0m'

        if len(self.dates) == 0:
            print("Error: Please run model before displaying stats")
            return

        print(f'{bld}Stats{end}')
        print("Stock(s):")
        i = 0
        for stock in self.stocks:
            print(f'{stock} | ',
                  f"Training: {self.dates[i][0]}-{self.dates[i][1]}",
                  f"Testing: {self.dates[i][2]}-{self.dates[i][3]}")
            i += 1

        print(f"\nTotal Buys: {self.totalBuys}")
        prnt = None
        if self.buyStats() > 50:
            prnt = f"{gre}{self.buyStats()}%{end}"
        elif self.buyStats() < 50:
            prnt = f"{red}{self.buyStats()}%{end}"
        else:
            prnt = f"{self.buyStats()}%"
        print(f"Buy Accuracy: {prnt}")
        print(f"Total Sells: {self.totalSells}")

        if self.sellStats() > 50:
            prnt = f'{gre}{self.sellStats()}%{end}'
        elif self.sellStats() < 50:
            prnt = f'{red}{self.sellStats()}%{end}'
        else:
            prnt = f'{self.sellStats()}%'
        print(f"Sell Accuracy: {prnt}")

    def visualizeModel(self, width=5, height=5, stepsize=0.02):
        """Output a visualization of the backtesting results.

        The diagram overlays training and testing observations on top of
        a color coded representation of learned recommendations. The color
        intensity represents the distribution of probability.
        """
        import matplotlib.pyplot as plt
        from matplotlib.colors import ListedColormap
        if len(self.variables) != 2:
            print("Error: Plotting is restricted to 2 dimensions")
            return
        if (self.XX is None or self.yy is None or self.model is None):
            print("Error: Please run model before visualizing")
            return

        X, y = self.XX, self.yy
        X = StandardScaler().fit_transform(X)
        self.model.fit(X, y)
        x_min, x_max = X[:, 0].min() - 0.5, X[:, 0].max() + 0.5
        y_min, y_max = X[:, 1].min() - 0.5, X[:, 1].max() + 0.5
        xx, yy = meshgrid(
            arange(x_min, x_max, stepsize), arange(y_min, y_max, stepsize)
            )

        plt.figure(figsize=(width, height))
        cm = plt.cm.RdBu
        RedBlue = ListedColormap(['#FF312E', '#6E8894'])
        Axes = plt.subplot(1, 1, 1)
        Z = self.model.decision_function(c_[xx.ravel(), yy.ravel()])
        Z = Z.reshape(xx.shape)

        stock = self.stocks[len(self.stocks)-1]
        Axes.set_title(stock)
        Axes.contourf(xx, yy, Z, cmap=cm, alpha=0.75)
        Axes.scatter(X[:, 0], X[:, 1], c=y, cmap=RedBlue)
        Axes.set_xlim(xx.min(), xx.max())
        Axes.set_ylim(yy.min(), yy.max())
        plt.savefig(stock+'.svg', format='svg')
