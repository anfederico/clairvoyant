from sklearn.svm import SVC
from sklearn.preprocessing import StandardScaler
from numpy import vstack, hstack
from pytz import timezone
from pandas import to_datetime
from clairvoyant.utils import DateIndex, FindConditions, PercentChange

class Clair:
    """
    Cla.I.R. - Classifier Inferred Recommendations
    Clair uses the support vector machine supplied by the sklearn library to
    to infer buy and sell classifications for stocks using a client-supplied
    feature specification.
    """
    def __init__(self, variables, trainStart, trainEnd, testStart, testEnd,
                 buyThreshold = 0.65, sellThreshold = 0.65, C = 1, gamma = 10,
                 continuedTraining = False, tz=timezone('UTC')):

        # Conditions
        self.variables = variables
        self.trainStart = tz.localize(to_datetime(trainStart))
        self.trainEnd = tz.localize(to_datetime(trainEnd))
        self.testStart = tz.localize(to_datetime(testStart))
        self.testEnd = tz.localize(to_datetime(testEnd))
        self.buyThreshold = buyThreshold
        self.sellThreshold = sellThreshold
        self.C = C
        self.gamma = gamma
        self.continuedTraining  = continuedTraining

    def learn(self, data, X=[], y=[]):
        trainStart = DateIndex(data, self.trainStart, False)
        trainEnd = DateIndex(data, self.trainEnd, True)

        for i in range(trainStart, trainEnd+1):             # Training period

            Xs = []
            for var in self.variables:                      # Handles n variables
                Xs.append(FindConditions(data, i, var))     # Find conditions for Period 1
            X.append(Xs)

            y1 = PercentChange(data, i+1)                   # Find the stock price movement for Period 2
            if y1 > 0: y.append(1)                          # If it went up, classify as 1
            else:      y.append(0)                          # If it went down, classify as 0

        XX = vstack(X)                                      # Convert to numpy array
        yy = hstack(y)                                      # Convert to numpy array

        model = SVC(C=self.C, gamma=self.gamma, probability=True)
        model.fit(XX, yy)

        return model, X, y

    def predict(self, model, Xs):
        prediction = model.predict_proba([Xs])[0]
        negative = prediction[0]
        positive = prediction[1]
        return positive, negative

    def test(self, data, model, X=[], y=[]):
        testStart = DateIndex(data, self.testStart, False)
        testEnd = DateIndex(data, self.testEnd, True)

        period = testStart
        while period < testEnd:
            Xs = []
            for var in self.variables:
                Xs.append(FindConditions(data, period, var))

            pos, neg = self.predict(model, Xs)

            if   pos >= self.buyThreshold:  prediction =  1      # If positive confidence >= buyThreshold, predict buy
            elif neg >= self.sellThreshold: prediction = -1      # If negative confidence >= sellThreshold, predict sell
            else: prediction = 0

            if prediction == 1:
                self.buyLogic(self, pos, data, period)

            elif prediction == -1:
                self.sellLogic(self, neg, data, period)

            period += 1

            nextPeriodPerformance = PercentChange(data, period)
            self.nextPeriodLogic(
                self, prediction, nextPeriodPerformance, data, period
                )

            if self.continuedTraining == True:

                X.append(Xs)

                if nextPeriodPerformance > 0:
                    y.append(1)
                else:
                    y.append(0)

                XX = vstack(X)
                yy = hstack(y)
                model.fit(XX, yy)

    def buyLogic(self, prob, data, testPeriod):
        print(f'{data["Date"][testPeriod]}: buy with {prob} probability')

    def sellLogic(self, prob, data, testPeriod):
        print(f'{data["Date"][testPeriod]}: sell with {prob} probability')

    def nextPeriodLogic(self, prediction, performance, data, testPeriod):
        pass
