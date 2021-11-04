from src.estimators.example import ExampleEstimator, Example2Estimator, FirstEstimator
from src.example_pipelines.pipelines_example import SVM_Pipeline, EmptyPipeline
from src.pipelines import PipelinesManager
from src.estimators.Bert import Bert
import pandas as pd

if __name__ == "__main__":
    df = pd.read_csv("cola_public_1.1/cola_public/raw/in_domain_train.tsv", delimiter="\t",
                     header=None, names=["sentence_source", "label", "label_notes", "sentence"])

    X = df.sentence.values
    y = df.label.values

    Bert(model="bert-base-uncased", lock_gpu=True, path_to_save_stats="stats", path_to_save_model="model").fit(X, y)