from matplotlib.colors import ListedColormap
from matplotlib import pyplot
from bokeh.plotting import output_file, figure, show
from numpy import meshgrid, arange, c_
from model import SciKitModel as Model

# Local imports

from clairvoyant import exchange, helpers

import sys
sys.path.append("..")


class Engine:
    def __init__(self, features, train_str, train_end, test_str, test_end,
                 buy_threshold=0.65,
                 sell_threshold=0.65,
                 continue_training=False,
                 total_buys=0,
                 correct_buys=0,
                 total_sells=0,
                 correct_sells=0):
        self.model = None
        self.account = None
        self.data = None
        self.features = features
        self.train_str = train_str
        self.train_end = train_end
        self.test_str = test_str
        self.test_end = test_end
        self.buy_threshold = buy_threshold
        self.sell_threshold = sell_threshold
        self.continue_training = continue_training
        self.total_buys = total_buys
        self.correct_buys = correct_buys
        self.total_sells = total_sells
        self.correct_sells = correct_sells

    def start(self, data, capital=None, logic=None, simulation=False, **kwargs):
        self.data = data
        self.model = Model(**kwargs)

        # ====================== #
        #    Initial Training    #
        # ====================== #
        
        X, y = [], []                                   
        for i in range(self.train_str, self.train_end+1):

            Xs = [data.iloc[i][var] for var in self.features]
            X.append(Xs)                             
            
            # Find the stock price movement for day 2
            y1 = helpers.change(data.iloc[i+1].open, data.iloc[i+1].close)
            if y1 > 0:
                y.append(1)  # If it went up, classify as 1
            else:
                y.append(-1) # If it went down, classify as -1
        
        self.model.fit(X, y)

        # ====================== #
        #         Testing        #
        # ====================== #       
        
        if simulation:
            self.account = exchange.Account(capital)

        for i in range(self.test_str, self.test_end):
            
            # ==================================== #
            #  DAY 1 @ 8:00 PM | Markets closed    #
            #  Make prediction for DAY 2           #
            #  Update Buy/Sell count (or neither)  #
            # ==================================== #        
            
            Xs = [data.iloc[i][var] for var in self.features]
            neg, pos = self.model.predict(Xs)
            
            if pos >= self.buy_threshold:  # Positive confidence >= buyThreshold
                prediction = 1
                confidence = pos
            
            elif neg >= self.sell_threshold: # If negative confidence >= sellThreshold
                prediction = -1
                confidence = neg

            else:
                prediction = 0
                confidence = 0
            
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
                    self.total_buys += 1
                    if helpers.change(data.iloc[i+1].open, data.iloc[i+1].close) > 0:
                        self.correct_buys += 1
                
                # Case 3/4: Prediction is negative (sell), next day performance is/isn't negative
                elif prediction == -1:
                    self.total_sells += 1
                    if helpers.change(data.iloc[i+1].open, data.iloc[i+1].close) < 0:
                        self.correct_sells += 1
            
            # ====================== #
            #     Update Model       #
            #     if specified       #
            # ====================== #
            
            if self.continue_training:
                X.append(Xs)     
                
                if change(data, i+1) > 0:
                    y.append(1)
                else:
                    y.append(-1)
                
                self.model.fit(X, y)

    def conditions(self):
        if self.model is None:
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
        print("Training: {0} -- {1}".format(self.data.iloc[self.train_str].date, self.data.iloc[self.train_end].date))
        print("Testing:  {0} -- {1}".format(self.data.iloc[self.test_str].date, self.data.iloc[self.test_end].date))
        print("Buy Threshold: {0}%".format(self.buy_threshold*100))
        print("Sell Threshold: {0}%".format(self.sell_threshold*100))
        print("Continued Training: {0}".format(self.continue_training))
        print("\n---------------------------------------\n")

    def visualize(self, name, width=5, height=5, stepsize=0.02):
        if len(self.features) != 2:
            print("Error: Plotting is restricted to 2 dimensions")
            return
        if self.model is None:
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
    def __init__(self, features, train_str, train_end, test_str, test_end,
                 buy_threshold=0.65, sell_threshold=0.65, continue_training=False):
        Engine.__init__(self, features, train_str, train_end, test_str, test_end,
                        buy_threshold, sell_threshold, continue_training)
        
    def start(self, data, **kwargs):
        Engine.start(self, data, **kwargs)
                        
    def buy_stats(self):
        try:
            return round((float(self.correct_buys)/self.total_buys)*100,2)
        except ZeroDivisionError:
            return float(0)

    def sell_stats(self):
        try:
            return round((float(self.correct_sells)/self.total_sells)*100,2)
        except ZeroDivisionError:
            return float(0)

    def statistics(self):        
        if self.model is None:
            print("Error: Please start model to generate statistics")
            return

        print("------------- Statistics --------------\n")
        print("Total Buys: {0}".format(self.total_buys))
        print("Buy Accuracy: {0}%".format(self.buy_stats()))
        print("Total Sells: {0}".format(self.total_sells))
        print("Sell Accuracy: {0}%".format(self.sell_stats))
        print("\n---------------------------------------\n")


class Simulation(Engine):
    def __init__(self, features, train_str, train_end, test_str, test_end,
                 buy_threshold=0.65,
                 sell_threshold=0.65,
                 continue_training=False):
        Engine.__init__(self, features, train_str, train_end, test_str, test_end,
                        buy_threshold, sell_threshold, continue_training)

    def start(self, data, capital, logic, **kwargs):
        Engine.start(self, data, capital=capital, logic=logic, simulation=True, **kwargs)        

    def statistics(self):          
        print("------------- Statistics --------------\n")
        begin_price = self.data.iloc[self.test_str]['open']
        final_price = self.data.iloc[self.test_end]['close']

        percent_change = helpers.change(begin_price, final_price)
        print("Buy and Hold : {0}%".format(round(percent_change*100, 2)))
        print("Net Profit   : {0}".format(round(helpers.profit(self.account.InitialCapital, percent_change), 2)))
        
        percent_change = helpers.change(self.account.InitialCapital, self.account.TotalValue(final_price))
        print("Strategy     : {0}%".format(round(percent_change*100, 2)))
        print("Net Profit   : {0}".format(round(helpers.profit(self.account.InitialCapital, percent_change), 2)))

        longs = len([T for T in self.account.OpenedTrades if T.Type == 'Long'])
        sells = len([T for T in self.account.ClosedTrades if T.Type == 'Long'])
        shorts = len([T for T in self.account.OpenedTrades if T.Type == 'Short'])
        covers = len([T for T in self.account.ClosedTrades if T.Type == 'Short'])

        print("longs        : {0}".format(longs))
        print("Sells        : {0}".format(sells))
        print("Shorts       : {0}".format(shorts))
        print("Covers       : {0}".format(covers))
        print("--------------------")
        print("Total Trades : {0}".format(longs+sells+shorts+covers))
        print("\n---------------------------------------\n")

    def chart(self, name):
        output_file("{0}.html".format(name), title="Equity Curve")
        p = figure(x_axis_type="datetime", plot_width=1000, plot_height=400, title="Equity Curve")
        p.grid.grid_line_alpha = 0.3
        p.xaxis.axis_label = 'Date'
        p.yaxis.axis_label = 'Equity'
        
        shares = self.account.InitialCapital/self.data.iloc[self.test_str].open
        base_equity = [Price*shares for Price in self.data[self.test_str:self.test_end].open]
        
        p.line(self.data[self.test_str:self.test_end].date, base_equity, color='#CAD8DE', legend='Buy and Hold')
        p.line(self.data[self.test_str:self.test_end].date, self.account.Equity, color='#49516F', legend='Strategy')
        p.legend.location = "top_left"
        show(p)
