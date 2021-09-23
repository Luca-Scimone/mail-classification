from abc import ABC, abstractmethod

from class_mails.class_mails import Mails, Data

""" 
PipelinesManager and BasePipeline MUST BE independant from any implementation (SKLEARN for example).
PipelinesManager acts on BasePipeline abstract class. 
"""


class PipelinesManager:
    """
    Notice that a PipelinesManager share some data to train between every pipeline. Shared Data MUST BE NOT
    changed at runtime. To predict some data, you can pass proper data in your BasePipeline inherited
    class or predict over shared data. If you predict over shared data, shared data MUST NOT BE changed.
    """

    def __init__(self, path="", encoding='cp1252', header=True):
        self.pipelines = dict()
        self._data = Mails()  # READ ONLY
        self._read_data(path, encoding, header)
        print("Your data is : ", self.data, "\n End")
        self._name = 'name'
        self.nb_pipelines = 0

    @property
    def data(self):
        return self._data

    @data.setter
    def data(self, data):
        print("DATA FROM MANAGER IS READ ONLY.")

    def get_name(self):
        return self._name

    # Call the set mails of the Mails classe
    def _read_data(self, path, encoding, header):
        self._data.set(path, encoding, header)

    # pipeline is a subclass of BasePipeline
    def register_pipeline(self, pipeline, name='default'):

        if name == 'default':
            name = self.nb_pipelines

        if name not in self.pipelines:
            self.pipelines[name] = pipeline
            # self.pipelines.set_data(self._data)  # pass shared data to the pipeline
        else:
            print("WARNING: The pipeline ", name, " has already been added. ")

        self.nb_pipelines += 1



    """ 
    Launch fit for every pipelines in the Job Manager. 
    """

    def fit(self):
        for pipeline in self.pipelines:
            pipeline.fit()

    """
    Launch transform for every pipeline in the Job Manager. Add multithreading support. 
    """

    def transform(self):
        for pipeline in self.pipelines:
            pipeline.transform()

    # TODO Add multithreading support. Don't use this method
    def execute(self):
        for pipeline in self.pipelines:
            pipeline.execute()


""" 
This class provide a way to define a custom Pipeline. 
This a an abstract classes that is not intended to be instantiated. 
If you want a more consistent base pipeline, you can subclass EmptyPipeline.
"""


class BasePipeline(ABC):

    def __init__(self):
        self._shared_data = None
        self._pipeline = None

    @property
    def shared_data(self):
        return self._shared_data

    @shared_data.setter
    def shared_data(self, data: Data):
        self._shared_data = data

    @property
    @abstractmethod
    def pipeline(self):
        pass

    @pipeline.setter
    @abstractmethod
    def pipeline(self, pipeline):
        pass

    """ 
    Call fit method of each estimator of the pipeline.
    """

    @abstractmethod
    def fit(self, x, y):
        pass

    """ 
    Call transform method of each estimator of the pipeline.
    """

    @abstractmethod
    def transform(self, data):
        pass

    """ 
    Abstract method.
    Dump the model in a file. This function should also keep the estimators name of the pipeline 
    and the parameters.
    Must return an error if dump is called but self.pipeline was not train.
    """

    @abstractmethod
    def dump(self, path):
        pass

    """ 
    Abstract method.
    Load the model from file. This function should reload the estimators of the pipeline and the parameters.
    """

    @abstractmethod
    def load(self, path):
        pass

    """ 
    Predict labels from the model. Must return an error if predict is called but self.pipeline was not train.
    TO DISCUSS : This method take a Data. It doesnt take transformed data.
    It must return a dictionnary with the original data and associated label. 
    return {"data": your_data, "label": your_label}
    your_data and your_label must be the same size and provide both iterators. 
    """

    @abstractmethod
    def predict(self, data: Data):
        pass

    """ 
    For future. This class define what will be execute in parallel with the PipelinesManager. 
    """
    @abstractmethod
    def execute(self):
        pass

    """ 
    Give a demo of your pipeline. So others users can see how wonderful is your pipeline.
    """

    @abstractmethod
    def demo(self):
        pass
