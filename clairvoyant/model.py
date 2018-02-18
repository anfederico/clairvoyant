from sklearn.svm           import SVC
from sklearn.preprocessing import RobustScaler
from numpy                 import vstack, hstack

# Abstract model class to support any machine learning APIs
class Model:
    def __init__(self, **kwargs):
        raise NotImplementedError

    def fit(self, X, y):
        raise NotImplementedError

    def predict(self, Xs):
        raise NotImplementedError

class SciKitModel(Model):
    def __init__(self, **kwargs):
        self.kwargs = kwargs
        self.svc = SVC(**kwargs, probability=True)

    def fit(self, X, y):
        self.XX = vstack(X)
        self.yy = hstack(y)
        self.scaler = RobustScaler().fit(self.XX)
        self.svc.fit(self.scaler.transform(self.XX), self.yy)

    def predict(self, Xs):
        prediction = self.svc.predict_proba(self.scaler.transform([Xs]))[0]
        return prediction[0], prediction[1] # Negative, Positive