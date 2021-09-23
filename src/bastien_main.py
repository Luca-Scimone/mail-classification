import numpy as np
import seaborn as sns
from matplotlib import pyplot as plt
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import confusion_matrix, accuracy_score
from sklearn.model_selection import train_test_split
from sklearn.svm import SVC

from estimators.preprocessing import Lemme, Purge
from example_pipelines.pipelines_example import SVM_Pipeline, EmptyPipeline
from pipelines import PipelinesManager

if __name__ == "__main__":
    # Always instantiate the PipelineManager first ! It contains shared data and soon it will permit to parallelize
    # some tasks
    manager = PipelinesManager(path="mails.csv")
    my_pipeline = EmptyPipeline()
    my_pipeline.pipeline = [Lemme(), TfidfVectorizer(), SVC()]  # Give your pipeline
    x_train, x_test, y_train, y_test = train_test_split(manager.data.mails_df()['corps'], manager.data.labels_ls())

    out = my_pipeline.fit(x_train, y_train)
    predictions = my_pipeline.predict(x_test)

    round_predictions = np.around(predictions)
    mat_r = confusion_matrix(round_predictions, y_test)
    sns.heatmap(mat_r, square=True, annot=True, fmt="d")
    plt.xlabel("true labels")
    plt.ylabel("predicted label")
    plt.show()
    print("The accuracy with RTF is {}".format(accuracy_score(y_test, round_predictions)))
    # print(out)
    # my_pipeline.show_confusion_matrix()
