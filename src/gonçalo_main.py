from estimators.example import ExampleEstimator, Example2Estimator, FirstEstimator
from example_pipelines.pipelines_example import SVM_Pipeline, EmptyPipeline
from pipelines import PipelinesManager

if __name__ == "__main__":
    # Always instantiate the PipelineManager first ! It contains shared data and soon it will permit to parallelize
    # some tasks
    manager = PipelinesManager("mails.csv")

    # First example, you can instantiate a high pipeline_example
    svm_pipeline = SVM_Pipeline()
    svm_pipeline.shared_data = manager.data  # set data for training
    svm_pipeline.demo()  # Run your demo defined in svm_pipeline

    # Maybe you want to define your pipeline. It is not the best way to do so. You can rather inherited
    # Empty_Pipeline in pipelines_example. This main must stay as short as possible.
    my_pipeline = EmptyPipeline()
    my_pipeline.shared_data = manager.data  # set data for training
    my_pipeline.pipeline = (FirstEstimator(), ExampleEstimator(), Example2Estimator())  # Give your pipeline
    my_pipeline.transform()
    my_pipeline.show_confusion_matrix()
