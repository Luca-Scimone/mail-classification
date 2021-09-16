from src.class_mails.class_mails import Mails
from sklearn.pipeline import Pipeline

class PipelinesManager:

    def __init__(self, path=""):
        self.classifiers = dict()
        self.data = Mails()
        self._read_data(path=path)

    def _read_data(self):
        self.data.read_mails()

    def add_pipeline(self):
        return Pipeline()

class Pipeline:
    def __init__(self, data, parameters={}):
        self.data = data
        self.parameters = parameters
        self.pipeline = None

    def make_pipeline(self, list):
        self.pipeline =

    def fit(self):
        pass

    def transform(self):
        pass





