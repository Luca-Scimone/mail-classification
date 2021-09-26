from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.svm import SVC

from estimators.preprocessing import Lemme, Purge
from example_pipelines.pipelines_example import SVM_Pipeline, EmptyPipeline
from pipelines import PipelinesManager

if __name__ == "__main__":
    manager = PipelinesManager(path="../mails.csv")
    my_pipeline = EmptyPipeline()
    my_pipeline.pipeline = [Lemme(), TfidfVectorizer(), SVC()]  # Give your pipeline
    x_train, x_test, y_train, y_test = train_test_split(manager.data.mails_df()['corps'], manager.data.labels_ls())
    out = my_pipeline.fit(x_train, y_train)
    my_pipeline.show_confusion_matrix(x_test, y_test)
    # print(out)
    # my_pipeline.show_confusion_matrix()
