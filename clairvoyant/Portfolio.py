from sklearn.svm           import SVC
from sklearn.preprocessing import StandardScaler
from pandas                import read_csv, to_datetime
from numpy                 import vstack, hstack
from csv                   import DictWriter
from pandas.tslib          import relativedelta
from dateutil.parser       import parse

def DateIndex(data, date, end):
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
    raise ValueError("Couldn't find "+date.strftime('%m/%d/%Y')+" or suitable alternative")
    
def FindConditions(data, day, indicator):
    return data[indicator][day]
    
def PercentChange(data, day):
    return (data["Close"][day] - data["Open"][day]) / data["Open"][day]

def Predict(model, Xs):
    prediction = model.predict_proba([Xs])[0]
    negative = prediction[0]
    positive = prediction[1]
    return negative, positive

class Portfolio:
    
    def __init__(self, variables, trainStart, trainEnd, testStart, testEnd, buyThreshold = 0.65, sellThreshold = 0.65, C = 1, gamma = 10, continuedTraining = False):
        
        # Conditions
        self.variables          = variables
        self.trainStart         = to_datetime(trainStart) 
        self.trainEnd           = to_datetime(trainEnd)
        self.testStart          = to_datetime(testStart)
        self.testEnd            = to_datetime(testEnd)
        self.buyThreshold       = buyThreshold
        self.sellThreshold      = sellThreshold
        self.C                  = C
        self.gamma              = gamma
        self.continuedTraining  = continuedTraining
        
        # Run
        self.startingBalance    = 0
        self.buyingPower        = 0
        self.shares             = 0
        self.lastQuote          = 0
        
        # All runs
        self.runs               = 0
        self.performances       = []
    
    def runModel(self, data, startingBalance, buyLogic, sellLogic, nextDayLogic):
    
        # Configure dates
        data['Date'] = to_datetime(data['Date'])
        
        trainStart = DateIndex(data, self.trainStart, False)
        trainEnd   = DateIndex(data, self.trainEnd, True)
        testStart  = DateIndex(data, self.testStart, False)
        testEnd    = DateIndex(data, self.testEnd, True)
        
        self.runs += 1
        
        # Portfolio
        self.startingBalance = startingBalance
        self.buyingPower = startingBalance
        self.shares = 0
        self.lastQuote = 0

        # ====================== #
        #    Initial Training    #
        # ====================== #
        
        X, y = [], []                                   
        for i in range(trainStart, trainEnd+1):             # Training period
            
            Xs = []
            for var in self.variables:                      # Handles n variables
                Xs.append(FindConditions(data, i, var))     # Find conditions for day 1
            X.append(Xs)                             
            
            y1 = PercentChange(data, i+1)                   # Find the stock price movement for day 2
            if y1 > 0: y.append(1)                          # If it went up, classify as 1
            else:      y.append(0)                          # If it went down, classify as 0
                
        XX = vstack(X)                                      # Convert to numpy array
        yy = hstack(y)                                      # Convert to numpy array
    
        model = SVC(C=self.C, gamma=self.gamma, probability=True)
        model.fit(XX, yy)
        
        # ====================== #
        #         Testing        #
        # ====================== #       
        
        testDay = testStart                                  
        while (testDay < testEnd):
            
            # ==================================== #
            #  DAY 1 @ 8:00 PM | Markets closed    #
            #  Make prediction for DAY 2           #
            #  Update Buy/Sell count (or neither)  #
            # ==================================== #        
            
            Xs = []
            for var in self.variables:
                Xs.append(FindConditions(data, testDay, var))
   
            neg, pos = Predict(model, Xs)
        
            if   pos >= self.buyThreshold:  prediction =  1      # If positive confidence >= buyThreshold, predict buy
            elif neg >= self.sellThreshold: prediction = -1      # If negative confidence >= sellThreshold, predict sell
            else: prediction = 0
            
            if prediction == 1:
                buyLogic(self, pos, data, testDay)
                
            elif prediction == -1:
                sellLogic(self, neg, data, testDay)
                
            testDay += 1
            
            # ==================================== #
            #  DAY 2 @ 4:30 PM | Markets closed    #
            #  Analyze results from DAY 2          #
            #  Record if prediction was correct    #
            # ==================================== #
            
            nextDayPerformance = PercentChange(data, testDay)
            
            nextDayLogic(self, prediction, nextDayPerformance, data, testDay)
            
            # ====================== #
            #     Update Model       #
            #     if specified       #
            # ====================== #
            
            if self.continuedTraining == True:

                X.append(Xs)    
                
                if nextDayPerformance > 0: y.append(1)       
                else:                      y.append(0)                    
                    
                XX = vstack(X)                                
                yy = hstack(y)            
                model.fit(XX, yy)

        # Record Performance
        self.lastQuote = FindConditions(data, testDay, "Close")
        self.performances.append(((self.portfolioValue(data, testDay)-self.startingBalance)/self.startingBalance)*100)

    def portfolioValue(self, data, testDay):
        quote = FindConditions(data, testDay, "Close")
        return self.buyingPower+self.shares*quote
    
    def buyShares(self, shares, quote):
        if (shares*quote) <= self.buyingPower:
            self.buyingPower -= shares*quote
            self.shares += shares  
        else: print "Sorry, insufficient buying power."    
    
    def sellShares(self, shares, quote):
        if shares <= self.shares:
            self.buyingPower += shares*quote
            self.shares -= shares    
        else: print "Sorry, you don't own this many shares."
    
    def displayLastRun(self):
        bld, gre, red, end = '\033[1m', '\033[92m', '\033[91m', '\033[0m'
   
        if self.runs < 1: print "Error: No last run"; return
        
        print bld+"Run #"+str(self.runs)+end
        print "Buying Power: $" + str(round(self.buyingPower,2)) 
        print "Shares: " + str(self.shares) 
        
        totalValue = round(self.buyingPower+self.shares*self.lastQuote,2)
        if totalValue > self.startingBalance:   print "Total Value: $" + gre+str(round(self.buyingPower+self.shares*self.lastQuote,2))+end
        elif totalValue < self.startingBalance: print "Total Value: $" + red+str(round(self.buyingPower+self.shares*self.lastQuote,2))+end            
        else:                                   print "Total Value: $" + str(round(self.buyingPower+self.shares*self.lastQuote,2)) 
        
    def displayAllRuns(self):
        bld, gre, red, end = '\033[1m', '\033[92m', '\033[91m', '\033[0m'

        print bld+"Performance across all runs"+end
        print "Runs: "+str(self.runs)
        
        try: averagePerformance = round(sum(self.performances)/len(self.performances),2)
        except ZeroDivisionError: print "Average Performance: None\n"; return
        
        if averagePerformance > 0:   print "Average Performance: "+gre+str(averagePerformance)+"%"+end
        elif averagePerformance < 0: print "Average Performance: "+red+str(averagePerformance)+"%"+end
        else:                        print "Average Performance: "+str(averagePerformance)+"%"
    
    def clearAllRuns(self):
        self.startingBalance = 0
        self.buyingPower = 0
        self.shares = 0
        self.lastQuote = 0        
        self.runs = 0
        self.performances = []     