from sklearn.base import BaseEstimator, TransformerMixin

"""
This file contain an example of estimator. An estimator inherits from BaseEstimator and trasnformerMixin 
and implements fit and transform method.
"""


class FirstEstimator(BaseEstimator, TransformerMixin):

    def fit(self, mails):
        return self

    def transform(self, mails):
        return mails


class ExampleEstimator(BaseEstimator, TransformerMixin):
    def fit(self):
        return self

    def transform(self, data):
        return data


class Example2Estimator(BaseEstimator, TransformerMixin):
    def fit(self):
        return self

    def transform(self, data):
        return data
