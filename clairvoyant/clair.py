"""Clair provides the machine learning brains behind Clairvoyant.

Classes defined by this module provide a framework for implementing machine
learning algorithms for stock data.
"""

from sklearn.svm import SVC
from numpy import vstack, hstack
from pytz import timezone
from pandas import to_datetime
from abc import ABCMeta, abstractmethod
from clairvoyant import History


class Strategy(metaclass=ABCMeta):
    """Strategy defines the common interface for implementing recommendations.

    Inherit from Strategy if your class is a type of classifier that determines
    buying and selling of shares and requires additional logic to respond to
    model-supplied recommendations.
    """

    @abstractmethod
    def buyLogic(self, prob, row, attrs):
        """Buy shares.

        :param prob: The probability of being in the buy classification.
        :param row: A named tuple containing a row from ``History`` data.
        :param attrs: A dict map of attribute names to common names.
        """
        assert(isinstance(row, tuple))
        assert(isinstance(attrs, dict))
        dt = getattr(row, attrs['Date'])
        print(f'[{dt}] buy with {prob} likelihood.')

    @abstractmethod
    def sellLogic(self, prob, row, attrs):
        """Sell shares.

        :param prob: The probability of being in the buy classification.
        :param row: A named tuple containing a row from ``History`` data.
        :param attrs: A dict map of attribute names to common names.
        """
        assert(isinstance(row, tuple))
        assert(isinstance(attrs, dict))
        dt = getattr(row, attrs['Date'])
        print(f'[{dt}] sell with {prob} likelihood.')

    @abstractmethod
    def nextPeriodLogic(self, prediction, performance, row, attrs):
        """Determine what to do next period.

        This is primarily used on testing data to retrospectively evaulate the
        effectiveness of buying and selling based on particular logic.

        :param prediction: A prediction of performance in the next period.
        :param performance: Actual stock performance in the next period.
        :param row: A named tuple containing a row from ``History`` data.
        :param attrs: A dict map of attribute names to common names.
        """
        assert(isinstance(row, tuple))
        assert(isinstance(attrs, dict))
        dt = getattr(row, attrs['Date'])
        print(f'[{dt}] prediction: {prediction}, performance: {performance}')


class Clair(Strategy):
    """Cla.I.R. - Classifier Inferred Recommendations.

    Clair uses the support vector machine supplied by the sk-learn library to
    to infer buy and sell classifications for stocks using a client-supplied
    feature specification. Clair uses the default Radial Basis Function kernel
    provided by SVC. For more details, see the `scikit learn documentation.
    <http://scikit-learn.org/stable/modules/svm.html#parameters-of-the-rbf-kernel>`_

    Clients need to provide a date range for the training phase and another
    range for the testing phase. The learning phase determines classification
    probabilities that are used in the testing phase.

    Once the model is reliably trained, clients may use the :func:`predict`
    function to predict a result given an observed support vector.

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
        self.continuedTraining = continuedTraining

    def learn(self, data, X=[], y=[]):
        """Start the learning phase.

        :param data: A ``History`` object containing stock data along with
                     training features.
        :param X: Optional preprocessed support vectors.
        :param y: Optional preprocessed target values. Should coincide with the
                  ``X`` parameter.
        """
        assert(isinstance(data, History))
        assert(len(X) == len(y))

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
        """Calculate the probability of a buy or sell classification.

        :param model: A trained model.
        :param Xs: A list containing support vector data for a single vector.
        """
        prediction = model.predict_proba([Xs])[0]
        negative = prediction[0]
        positive = prediction[1]
        return negative, positive

    def execute(self, data, model, X=[], y=[]):
        """Execute the strategy logic using a trained model and input data.

        :param data: A ``History`` object containing testing data.
        :param model: A trained model.
        :param X: Optional preprocessed support vectors used for continued
                  training.
        :param y: Optional preprocessed target values corresponding to any
                  supplied support vectors.
        """
        assert(isinstance(data, History))
        assert(len(X) == len(y))

        for row in data[self.testStart:self.testEnd]:
            Xs = []
            for var in self.variables:
                Xs.append(getattr(row, data._col_map[var]))

            neg, pos = self.predict(model, Xs)

            if pos >= self.buyThreshold:
                prediction = 1
            elif neg >= self.sellThreshold:
                prediction = -1
            else:
                prediction = 0

            if prediction == 1:
                self.buyLogic(pos, row, data._col_map)
            elif prediction == -1:
                self.sellLogic(neg, row, data._col_map)

            if row.Index < len(data)-1:
                nextPeriodPerformance = data.return_rate[row.Index + 1]
                self.nextPeriodLogic(
                    prediction, nextPeriodPerformance, row, data._col_map
                    )

            if self.continuedTraining is True:
                X.append(Xs)
                if nextPeriodPerformance > 0:
                    y.append(1)
                else:
                    y.append(0)
                XX = vstack(X)
                yy = hstack(y)
                model.fit(XX, yy)

    def buyLogic(self, prob, row, attrs):
        """Override this function to provide your own logic."""
        super().buyLogic(prob, row, attrs)

    def sellLogic(self, prob, row, attrs):
        """Override this function to provide your own logic."""
        super().sellLogic(prob, row, attrs)

    def nextPeriodLogic(self, prediction, performance, row, attrs):
        """Override this function to provide your own logic."""
        super().nextPeriodLogic(prediction, performance, row, attrs)
