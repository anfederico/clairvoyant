from sklearn.svm import SVC
from sklearn.preprocessing import StandardScaler
from numpy import vstack, hstack
from pytz import timezone
from pandas import to_datetime
from abc import ABCMeta, abstractmethod
from clairvoyant import History


class Strategy(metaclass=ABCMeta):
    """
    Defines a required interface for any classes which execute on a trained
    model. These functions determine how the class behaves in response to buy
    and sell triggers. These functions are intended to be overridden by child
    classes to implement client-specified logic.
    """
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

    :param variables: A list of feature columns to use for training. Must exist
                      in your data.
    :param trainStart: The starting datetime for training as a string.
                       ex: `'2017-02-23 06:30:00'`
    :param trainEnd: The ending datetime for training as a string.
    :param testStart: The starting datetime for model testing.
    :param testEnd: The ending datetime for model testing.
    :param buyThreshold: The confidence threshold for triggering buy logic.
    :param sellThreshold: The confidence threshold for triggering sell logic.
    :param C: Penalty parameter for learning algorithm. For noisy data, set to
              a number less than 1, but in general, 1.0 is suitable.
    :param gamma: Kernel coefficient for learning algorithm.
    :param continuedTraining: Determines if values observed in the testing
                              period will be used to further train the model.
    :param tz: The timezone associated with the datetime parameters.
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
        """
        Train the model using data.

        :param data: the data to use for training.
        :param X: additional support vectors to use with the data.
        :param y: additional target values to include with data.
        """
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
        """
        Use trained model to make a prediction on hypothetical support vectors.

        :param model: a trained model
        :param Xs: input support vectors
        """
        prediction = model.predict_proba([Xs])[0]
        negative = prediction[0]
        positive = prediction[1]
        return negative, positive

    def execute(self, data, model, X=[], y=[]):
        """
        Use a trained model to predict the next period's performance. Execute
        buy and sell logic in response to predictions.
        """
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
