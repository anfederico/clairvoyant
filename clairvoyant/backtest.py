import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from matplotlib.colors import ListedColormap
from numpy import meshgrid, arange, c_
from sklearn.preprocessing import StandardScaler
from numpy import vstack, hstack
from dateutil.parser import parse
from pytz import timezone
from clairvoyant.utils import DateIndex
from clairvoyant import Clair

class Backtest(Clair):
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
        stock = self.stocks[len(self.stocks)-1]

        # Learn and execute
        model, X, y = self.learn(data)
        self.execute(data, model, X, y)

        trainStart = DateIndex(data, self.trainStart, False)
        trainEnd = DateIndex(data, self.trainEnd, True)
        testStart = DateIndex(data, self.testStart, False)
        testEnd = DateIndex(data, self.testEnd, True)

        # Save for vizualization purposes
        self.dates.append([
            data['Date'][trainStart].strftime('%m/%d/%Y'),
            data['Date'][trainEnd].strftime('%m/%d/%Y'),
            data['Date'][testStart].strftime('%m/%d/%Y'),
            data['Date'][testEnd].strftime('%m/%d/%Y')
            ])

        XX = vstack(X)
        yy = hstack(y)
        self.XX    = XX
        self.yy    = yy
        self.model = model

    def buyLogic(self, prob, data, testPeriod, *args, **kwargs):
        self.totalBuys += 1
        if self.debug:
            super().buyLogic(prob, data, testPeriod, *args, **kwargs)

    def sellLogic(self, prob, data, testPeriod, *args, **kwargs):
        self.totalSells += 1
        if self.debug:
            super().sellLogic(prob, data, testPeriod, *args, **kwargs)

    def nextPeriodLogic(self, prediction, performance, *args, **kwargs):
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

    def buyStats(self):
        try:
            return round((float(self.correctBuys)/self.totalBuys)*100,2)
        except ZeroDivisionError:
            return float(0)

    def sellStats(self):
        try:
            return round((float(self.correctSells)/self.totalSells)*100,2)
        except ZeroDivisionError:
            return float(0)

    def displayConditions(self):
        bld, gre, red, end = '\033[1m', '\033[92m', '\033[91m', '\033[0m'

        print(bld+"Conditions"+end)
        i = 1
        for var in self.variables:
            print(("X%s: " % i)+var)
            i += 1

        print("Buy Threshold: "  + str(self.buyThreshold*100) + "%")
        print("Sell Threshold: " + str(self.sellThreshold*100) + "%")
        print("C: " + str(self.C))
        print("gamma: " + str(self.gamma))
        print("Continued Training: "+str(self.continuedTraining))
        print("Total Testing Periods: "+str(self.periods))
        print("Total Price Increases: "+str(self.increases))
        print("Total Price Decreases: "+str(self.decreases))

    def displayStats(self):
        bld, gre, red, end = '\033[1m', '\033[92m', '\033[91m', '\033[0m'

        if len(self.dates) == 0:
            print("Error: Please run model before displaying stats")
            return

        print(bld+"Stats"+end)
        print("Stock(s):")
        i = 0
        for stock in self.stocks:
            print(stock+' |',
                  "Training: "+self.dates[i][0]+'-'+self.dates[i][1],
                  "Testing: "+self.dates[i][2]+'-'+self.dates[i][3])
            i += 1

        print("\nTotal Buys: " + str(self.totalBuys))
        prnt = None
        if self.buyStats() > 50:
            prnt = gre+str(self.buyStats())+"%"+end
        elif self.buyStats() < 50:
            prnt = red+str(self.buyStats())+"%"+end
        else:
            prnt = str(self.buyStats())+"%"
        print("Buy Accuracy:", prnt)

        print("Total Sells: "   + str(self.totalSells))

        if self.sellStats() > 50:
            prnt = gre+str(self.sellStats())+"%"+end
        elif self.sellStats() < 50:
            prnt = red+str(self.sellStats())+"%"+end
        else:
            prnt = str(self.sellStats())+"%"
        print("Sell Accuracy:", prnt)

    def visualizeModel(self, width = 5, height = 5, stepsize = 0.02):

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
        xx, yy = meshgrid(arange(x_min, x_max, stepsize), arange(y_min, y_max, stepsize))

        plt.figure(figsize=(width, height))
        cm = plt.cm.RdBu
        RedBlue = ListedColormap(['#FF312E', '#6E8894'])
        Axes = plt.subplot(1,1,1)
        Z = self.model.decision_function(c_[xx.ravel(), yy.ravel()])
        Z = Z.reshape(xx.shape)

        stock = self.stocks[len(self.stocks)-1]
        Axes.set_title(stock)
        Axes.contourf(xx, yy, Z, cmap=cm, alpha=0.75)
        Axes.scatter(X[:, 0], X[:, 1], c=y, cmap=RedBlue)
        Axes.set_xlim(xx.min(), xx.max())
        Axes.set_ylim(yy.min(), yy.max())
        plt.savefig(stock+'.svg', format='svg')
