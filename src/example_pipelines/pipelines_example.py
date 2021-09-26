import numpy as np
from matplotlib import pyplot as plt
from sklearn.metrics import confusion_matrix, accuracy_score
from sklearn.pipeline import make_pipeline
import seaborn as sns

from class_mails.class_mails import Mails
from estimators.example import ExampleEstimator, Example2Estimator, FirstEstimator
from pipelines import BasePipeline

"""
The directory example_pipelines provide fast way to launch good pipelines that has been proved.
"""

"""
This class is the preferred way to create a custom pipeline. It gives default functions such as dump, load... 
If you are satisfied from your pipeline, you can 
add this pipeline to example_pipelines by inheriting EmptyPipeline.
"""


class EmptyPipeline(BasePipeline):
    """
    An EmptyPipeline has access to self.shared_data which is type Mails.
    """

    def __init__(self):
        # call init parent class
        super().__init__()

    @property
    def pipeline(self):
        return self._pipeline

    @pipeline.setter
    def pipeline(self, estimators):
        self._pipeline = make_pipeline(*estimators)

    """ 
    Call fit method of each estimator of the pipeline.
    """

    def fit(self, x, y):

        if self.pipeline is not None:
            self.pipeline.fit(x, y)
        else:
            print("Your pipeline is empty. Please provide a pipeline before running fit method.")

    """ 
    Call transform method of each estimator of the pipeline.
    """

    def transform(self, data):

        if self.pipeline is not None:
            out = self.pipeline.transform(data)
        else:
            print("Your pipeline is empty. Please provide a pipeline before running fit method.")
        return out

    """ 
    Dump the model in a file. This function should also keep the estimators name of the pipeline 
    and the parameters.
    Must return an error if dump is called but self.pipeline was not train.
    """

    # TODO
    def dump(self, path):
        pass

    """ 
    Load the model from file. This function should reload the estimators of the pipeline and the parameters.
    """

    # TODO
    def load(self, path):
        pass

    """ 
    Predict labels from the model. Must return an error if predict is called but self.pipeline was not train.
    """

    # TODO
    def predict(self, mails) -> list:
        # format des mails ?
        return self.pipeline.predict(mails)


    def show_confusion_matrix(self, x_test, y_test):
        """
        Show the confusion matrix over entry data and out data. You must train your pipeline before. y_test contain
        the real label of your data.
        """
        predictions = self.predict(x_test)
        round_predictions = np.around(predictions)
        mat_r = confusion_matrix(round_predictions, y_test)
        sns.heatmap(mat_r, square=True, annot=True, fmt="d")
        plt.xlabel("true labels")
        plt.ylabel("predicted label")
        plt.show()
        print("The accuracy with RTF is {}".format(accuracy_score(y_test, round_predictions)))

    """ 
    Give a demo of your pipeline. 
    """

    def demo(self):
        pass

    """ 
    Put the multi-threaded code here.
    """

    # TODO
    def execute(self):
        pass


class SVM_Pipeline(EmptyPipeline):
    """
    This pipeline gives a complete pipeline with one class SVM.
    Just call run method to make a demo.
    """

    def __init__(self):
        super().__init__()

    """ 
    Add here the code to run for SVM_pipeline
    """

    def demo(self):
        self.pipeline = (FirstEstimator(), ExampleEstimator(), Example2Estimator())  # Give a powerful default pipeline for your svm pipeline
        self.transform()  # call transform with shared_data
        # self.pipeline.fit()
        # Or maybe if the model already exist, we can load the model from disk. It's up to you to decide. You can also
        # load the model only if it already exists.
        # self.pipeline.load()
        # self.pipeline.predict(X) # predict over some mails
        self.show_confusion_matrix()  # show your result !
        # self.pipeline.dump()
