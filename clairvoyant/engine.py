from sklearn.svm           import SVC
from sklearn.preprocessing import RobustScaler
from matplotlib.colors     import ListedColormap
from matplotlib            import pyplot
from bokeh.plotting        import output_file, figure, show
from numpy                 import vstack, hstack, meshgrid, arange, c_, where

# Local imports
import sys
sys.path.append("..")
from clairvoyant import exchange, helpers

class Model:
    def __init__(self, **kwargs):
        self.kwargs = kwargs
        self.svc = SVC(probability=True, **kwargs)

    def fit(self, X, y):
        self.XX = vstack(X)
        self.yy = hstack(y)
        self.scaler = RobustScaler().fit(self.XX)
        self.svc.fit(self.scaler.transform(self.XX), self.yy)

    def predict(self, Xs):
        prediction = self.svc.predict_proba(self.scaler.transform([Xs]))[0]
        return prediction[0], prediction[1] # Negative, Positive

class Engine:
    def __init__(self, features, trainStr, trainEnd, testStr, testEnd, buyThreshold=0.65, sellThreshold=0.65, continueTraining=False):
        self.model            = None
        self.account          = None
        self.features         = features
        self.trainStr         = trainStr
        self.trainEnd         = trainEnd
        self.testStr          = testStr
        self.testEnd          = testEnd
        self.buyThreshold     = buyThreshold
        self.sellThreshold    = sellThreshold
        self.continueTraining = continueTraining

    def start(self, data, capital=None, logic=None, simulation=False, **kwargs):
        self.data = data
        self.model = Model(**kwargs)

        # ====================== #
        #    Initial Training    #
        # ====================== #
        
        X, y = [], []                                   
        for i in range(self.trainStr, self.trainEnd+1):

            Xs = [data.iloc[i][var] for var in self.features]
            X.append(Xs)                             
            
            # Find the stock price movement for day 2
            y1 = helpers.change(data.iloc[i+1].open, data.iloc[i+1].close)
            if y1 > 0: y.append(1)  # If it went up, classify as 1
            else:      y.append(-1) # If it went down, classify as -1
        
        self.model.fit(X, y)

        # ====================== #
        #         Testing        #
        # ====================== #       
        
        if simulation:
            self.account = exchange.Account(capital)

        for i in range(self.testStr, self.testEnd):
            
            # ==================================== #
            #  DAY 1 @ 8:00 PM | Markets closed    #
            #  Make prediction for DAY 2           #
            #  Update Buy/Sell count (or neither)  #
            # ==================================== #        
            
            Xs = [data.iloc[i][var] for var in self.features]
            neg, pos = self.model.predict(Xs)
            
            if pos >= self.buyThreshold:  # Positive confidence >= buyThreshold
                prediction =  1 
                confidence = pos
            
            elif neg >= self.sellThreshold: # If negative confidence >= sellThreshold
                prediction = -1
                confidence = neg

            else: prediction = confidence = 0
            
            if simulation:
                # Update account variables
                self.account.Date = data.iloc[i]['date']
                self.account.Equity.append(self.account.TotalValue(data.iloc[i]['close']))

                # Execute trading logic
                logic(self.account, data.iloc[i], prediction, confidence)

                # Cleanup empty positions
                self.account.PurgePositions()

            if not simulation:
                # ==================================== #
                #  DAY 2 @ 4:30 PM | Markets closed    #
                #  Analyze results from DAY 2          #
                #  Record if prediction was correct    #
                # ==================================== #
                
                # Case 1/2: Prediction is positive (buy), next day performance is/isn't positive 
                if prediction == 1:
                    self.totalBuys += 1
                    if helpers.change(data.iloc[i+1].open, data.iloc[i+1].close) > 0:
                        self.correctBuys += 1
                
                # Case 3/4: Prediction is negative (sell), next day performance is/isn't negative
                elif prediction == -1:
                    self.totalSells += 1
                    if helpers.change(data.iloc[i+1].open, data.iloc[i+1].close) < 0:
                        self.correctSells += 1
            
            # ====================== #
            #     Update Model       #
            #     if specified       #
            # ====================== #
            
            if self.continueTraining:
                X.append(Xs)     
                
                if change(data, i+1) > 0: y.append(1)
                else:                     y.append(-1)
                
                self.model.fit(X, y)

    def conditions(self):
        if self.model == None:
            print("Error: Please start model to generate conditions")
            return

        print("------------ Data Features ------------\n")
        for i, var in enumerate(self.features):
            print("X{0}: {1}".format(i+1, var))
        print("\n---------------------------------------\n")

        print("----------- Model Arguments -----------\n")
        for kwarg in self.model.kwargs: 
            print("{0}: {1}".format(kwarg, self.model.kwargs[kwarg]))
        print("\n---------------------------------------\n")

        print("---------  Engine Conditions ----------\n")
        print("Training: {0} -- {1}".format(self.data.iloc[self.trainStr].date, self.data.iloc[self.trainEnd].date))
        print("Testing:  {0} -- {1}".format(self.data.iloc[self.testStr].date, self.data.iloc[self.testEnd].date))
        print("Buy Threshold: {0}%".format(self.buyThreshold*100))
        print("Sell Threshold: {0}%".format(self.sellThreshold*100))
        print("Continued Training: {0}".format(self.continueTraining))
        print("\n---------------------------------------\n")

    def visualize(self, name, width=5, height=5, stepsize=0.02):
        if len(self.features) != 2:
            print("Error: Plotting is restricted to 2 dimensions")
            return
        if self.model == None:
            print("Error: Please start model before visualizing")
            return
            
        X, y = self.model.XX, self.model.yy # Retrieve previous XX and yy                                      
        X = self.model.scaler.transform(X)  # Normalize X values
        self.model.svc.fit(X, y)            # Refit model
        
        x_min, x_max = X[:, 0].min() - 0.5, X[:, 0].max() + 0.5    
        y_min, y_max = X[:, 1].min() - 0.5, X[:, 1].max() + 0.5     
        xx, yy = meshgrid(arange(x_min, x_max, stepsize), arange(y_min, y_max, stepsize))
        
        pyplot.figure(figsize=(width, height))
        cm = pyplot.cm.RdBu  # Red/Blue gradients
        rb = ListedColormap(['#FF312E', '#6E8894']) # Red = 0 (Negative) / Blue = 1 (Positve)
        Z = self.model.svc.decision_function(c_[xx.ravel(), yy.ravel()])
        Z = Z.reshape(xx.shape)
        
        Axes = pyplot.subplot(1,1,1)
        Axes.set_title(name)
        Axes.contourf(xx, yy, Z, cmap=cm, alpha=0.75)
        Axes.scatter(X[:, 0], X[:, 1], s=20, c=y, cmap=rb, edgecolors='black') 
        Axes.set_xlim(xx.min(), xx.max())
        Axes.set_ylim(yy.min(), yy.max())
        pyplot.savefig("{0}.png".format(name))

class Backtest(Engine):
    def __init__(self, features, trainStr, trainEnd, testStr, testEnd, buyThreshold=0.65, sellThreshold=0.65, continueTraining=False):
        Engine.__init__(self, features, trainStr, trainEnd, testStr, testEnd, buyThreshold, sellThreshold, continueTraining)

        # Statistics
        self.totalBuys    = 0
        self.correctBuys  = 0
        self.totalSells   = 0
        self.correctSells = 0
        
    def start(self, data, **kwargs):
        Engine.start(self, data, **kwargs)
                        
    def buyStats(self):
        try: return round((float(self.correctBuys)/self.totalBuys)*100,2)
        except ZeroDivisionError: return float(0)
        
    def sellStats(self):
        try: return round((float(self.correctSells)/self.totalSells)*100,2)
        except ZeroDivisionError: return float(0)

    def statistics(self):        
        if self.model == None:
            print("Error: Please start model to generate statistics")
            return

        print("------------- Statistics --------------\n")
        print("Total Buys: {0}".format(self.totalBuys))
        print("Buy Accuracy: {0}%".format(self.buyStats()))
        print("Total Sells: {0}".format(self.totalSells))
        print("Sell Accuracy: {0}%".format(self.sellStats()))
        print("\n---------------------------------------\n")

class Simulation(Engine):
    def __init__(self, features, trainStr, trainEnd, testStr, testEnd, buyThreshold=0.65, sellThreshold=0.65, continueTraining=False):
        Engine.__init__(self, features, trainStr, trainEnd, testStr, testEnd, buyThreshold, sellThreshold, continueTraining)

    def start(self, data, capital, logic, **kwargs):
        Engine.start(self, data, capital=capital, logic=logic, simulation=True, **kwargs)        

    def statistics(self):          
        print("------------- Statistics --------------\n")
        BeginPrice = self.data.iloc[self.testStr]['open']
        FinalPrice = self.data.iloc[self.testEnd]['close']

        percentchange = helpers.change(BeginPrice, FinalPrice)
        print("Buy and Hold : {0}%".format(round(percentchange*100, 2)))
        print("Net Profit   : {0}".format(round(helpers.profit(self.account.InitialCapital, percentchange), 2)))
        
        percentchange = helpers.change(self.account.InitialCapital, self.account.TotalValue(FinalPrice))
        print("Strategy     : {0}%".format(round(percentchange*100, 2)))
        print("Net Profit   : {0}".format(round(helpers.profit(self.account.InitialCapital, percentchange), 2)))

        Longs  = len([T for T in self.account.OpenedTrades if T.Type == 'Long'])
        Sells  = len([T for T in self.account.ClosedTrades if T.Type == 'Long'])
        Shorts = len([T for T in self.account.OpenedTrades if T.Type == 'Short'])
        Covers = len([T for T in self.account.ClosedTrades if T.Type == 'Short'])

        print("Longs        : {0}".format(Longs))
        print("Sells        : {0}".format(Sells))
        print("Shorts       : {0}".format(Shorts))
        print("Covers       : {0}".format(Covers))
        print("--------------------")
        print("Total Trades : {0}".format(Longs+Sells+Shorts+Covers))
        print("\n---------------------------------------\n")

    def chart(self, name):
        output_file("{0}.html".format(name), title="Equity Curve")
        p = figure(x_axis_type="datetime", plot_width=1000, plot_height=400, title="Equity Curve")
        p.grid.grid_line_alpha = 0.3
        p.xaxis.axis_label = 'Date'
        p.yaxis.axis_label = 'Equity'
        
        Shares = self.account.InitialCapital/self.data.iloc[self.testStr].open
        BaseEquity = [Price*Shares for Price in self.data[self.testStr:self.testEnd].open]      
        
        p.line(self.data[self.testStr:self.testEnd].date, BaseEquity, color='#CAD8DE', legend='Buy and Hold')
        p.line(self.data[self.testStr:self.testEnd].date, self.account.Equity, color='#49516F', legend='Strategy')
        p.legend.location = "top_left"
        show(p)