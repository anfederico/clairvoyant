from sklearn.svm import SVC
from sklearn.preprocessing import StandardScaler
from numpy import vstack, hstack
from pytz import timezone
from pandas import to_datetime
from clairvoyant.utils import DateIndex, FindConditions, PercentChange
from abc import ABCMeta, abstractmethod


class Strategy(metaclass=ABCMeta):
    @abstractmethod
    def buyLogic(self, prob, data, period):
        print(f'{data["Date"][period]}: buy with {prob} likelihood.')

    @abstractmethod
    def sellLogic(self, prob, data, period):
        print(f'{data["Date"][period]}: sell with {prob} likelihood.')

    @abstractmethod
    def nextPeriodLogic(self, prediction, performance, data, period):
        print(
            f'[{data["Date"][period]}] prediction: {prediction}, ',
            f'performance: {performance}'
            )


class Clair(Strategy):
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

        for i in range(trainStart, trainEnd+1):
            Xs = []
            for var in self.variables:
                Xs.append(FindConditions(data, i, var))
            X.append(Xs)

            y1 = PercentChange(data, i+1)
            if y1 > 0:
                y.append(1)
            else:
                y.append(0)

        XX = vstack(X)
        yy = hstack(y)

        model = SVC(C=self.C, gamma=self.gamma, probability=True)
        model.fit(XX, yy)

        return model, X, y

    def predict(self, model, Xs):
        prediction = model.predict_proba([Xs])[0]
        negative = prediction[0]
        positive = prediction[1]
        return negative, positive

    def execute(self, data, model, X=[], y=[]):
        testStart = DateIndex(data, self.testStart, False)
        testEnd = DateIndex(data, self.testEnd, True)

        period = testStart
        while period < testEnd:
            Xs = []
            for var in self.variables:
                Xs.append(FindConditions(data, period, var))

            neg, pos = self.predict(model, Xs)

            if   pos >= self.buyThreshold:
                prediction =  1
            elif neg >= self.sellThreshold:
                prediction = -1
            else:
                prediction = 0

            if prediction == 1:
                self.buyLogic(pos, data, period)
            elif prediction == -1:
                self.sellLogic(neg, data, period)

            period += 1

            nextPeriodPerformance = PercentChange(data, period)
            self.nextPeriodLogic(
                prediction, nextPeriodPerformance, data, period
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

    def buyLogic(self, prob, data, period):
        super().buyLogic(prob, data, period)

    def sellLogic(self, prob, data, period):
        super().sellLogic(prob, data, period)

    def nextPeriodLogic(self, prediction, performance, data, period):
        super().nextPeriodLogic(prediction, performance, data, period)
