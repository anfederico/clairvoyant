from sklearn.svm import SVC
from sklearn.preprocessing import StandardScaler
from numpy import vstack, hstack
from pytz import timezone
from pandas import to_datetime
from abc import ABCMeta, abstractmethod
from clairvoyant import History


class Strategy(metaclass=ABCMeta):
    @abstractmethod
    def buyLogic(self, prob, row, attrs):
        assert(isinstance(row, tuple))
        assert(isinstance(attrs, dict))
        dt = getattr(row, attrs['Date'])
        print(f'[{dt}] buy with {prob} likelihood.')

    @abstractmethod
    def sellLogic(self, prob, row, attrs):
        assert(isinstance(row, tuple))
        assert(isinstance(attrs, dict))
        dt = getattr(row, attrs['Date'])
        print(f'[{dt}] sell with {prob} likelihood.')

    @abstractmethod
    def nextPeriodLogic(self, prediction, performance, row, attrs):
        assert(isinstance(row, tuple))
        assert(isinstance(attrs, dict))
        dt = getattr(row, attrs['Date'])
        print(f'[{dt}] prediction: {prediction}, performance: {performance}')


class Clair(Strategy):
    """
    Cla.I.R. - Classifier Inferred Recommendations
    Clair uses the support vector machine supplied by the sklearn library to
    to infer buy and sell classifications for stocks using a client-supplied
    feature specification.
    """
    def __init__(self, variables, trainStart, trainEnd, testStart, testEnd,
                 buyThreshold=0.65, sellThreshold=0.65, C=1, gamma=10,
                 continuedTraining=False, tz=timezone('UTC')):

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
        assert(isinstance(data, History))

        for row in data[self.trainStart:self.trainEnd]:
            Xs = []
            for var in self.variables:
                Xs.append(getattr(row, data._col_map[var]))
            X.append(Xs)

            i = row.Index
            y1 = data.return_rate[i+1]
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
        assert(isinstance(data, History))

        for row in data[self.testStart:self.testEnd]:
            Xs = []
            for var in self.variables:
                Xs.append(getattr(row, data._col_map[var]))

            neg, pos = self.predict(model, Xs)

            if   pos >= self.buyThreshold:
                prediction =  1
            elif neg >= self.sellThreshold:
                prediction = -1
            else:
                prediction = 0

            if prediction == 1:
                self.buyLogic(pos, row, data._col_map)
            elif prediction == -1:
                self.sellLogic(neg, row, data._col_map)

            if row.Index < len(data)-1:
                period = row.Index + 1
                nextPeriodPerformance = data.return_rate[period]
                self.nextPeriodLogic(
                    prediction, nextPeriodPerformance, row, data._col_map
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

    def buyLogic(self, prob, row, attrs):
        super().buyLogic(prob, row, attrs)

    def sellLogic(self, prob, row, attrs):
        super().sellLogic(prob, row, attrs)

    def nextPeriodLogic(self, prediction, performance, row, attrs):
        super().nextPeriodLogic(prediction, performance, row, attrs)
