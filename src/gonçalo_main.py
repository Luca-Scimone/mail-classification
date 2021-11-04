from example_pipelines.pipelines_example import EmptyPipeline
from pipelines import PipelinesManager

if __name__ == "__main__":
    # Always instantiate the PipelineManager first ! It contains shared data
    # and soon it will permit to parallelize some tasks
    manager = PipelinesManager("mails.csv")

    print(manager.data.mails[0].label())
    print(manager.data.mails[1].label())
    print(manager.data.mails[2].label())

    print(manager.data.labels_ls())

    pret_pipeline = EmptyPipeline()

    pret_pipeline.shared_data = manager.data

    pret_pipeline.pipeline = [ToDataFrame()]

    out = pret_pipeline.transform()

    print(out)
