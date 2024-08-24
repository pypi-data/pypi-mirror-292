#!/usr/bin/env python3
"""Evaluate a pretrained local model on local data."""
import logging
from typing import cast

import fire
import pandas as pd
import yaml

from bitfount import config
from bitfount.data.datasources.dataframe_source import DataFrameSource
from bitfount.data.datastructure import DataStructure
from bitfount.data.schema import BitfountSchema
from bitfount.federated.utils import _MODELS
from bitfount.metrics import MetricCollection
from bitfount.transformations.dataset_operations import (
    CleanDataTransformation,
    NormalizeDataTransformation,
)
from bitfount.transformations.processor import TransformationProcessor
from bitfount.types import EvaluateReturnType

config._BITFOUNT_CLI_MODE = True


def evaluate_model(
    path_to_config_yaml: str, path_to_test_csv: str, path_to_model: str
) -> None:
    """Evaluates a model's performance.

    Args:
        path_to_config_yaml: Path to the config YAML file.
        path_to_test_csv: Path to the test CSV file.
        path_to_model: Path to the model file.
    """
    with open(path_to_config_yaml) as f:
        config = yaml.safe_load(f)
    algorithm = config.pop("algorithm")
    schema_filename = config.pop("schema")
    batch_size = config.get("batch_size")
    datasource_args = config["datasource_args"]
    target = config["target"]

    # Load dataset
    data = pd.read_csv(path_to_test_csv)
    schema = BitfountSchema.load_from_file(schema_filename)
    if len(schema.tables) > 1:
        raise ValueError("Only single-table schemas are supported.")

    datasource = DataFrameSource(data=data, **datasource_args)
    # Transform dataset
    clean_data = CleanDataTransformation()
    normalize = NormalizeDataTransformation()
    processor = TransformationProcessor([clean_data, normalize], schema.tables[0])
    datasource.data = processor.transform(datasource.data)

    # Create datastructure and get test dataloader
    data_structure = DataStructure(target=target, table=schema.table_names[0])
    # TODO: [BIT-1167] process transformations here

    # Load model
    neural_network = _MODELS[algorithm](datastructure=data_structure, schema=schema)
    neural_network.initialise_model(data=datasource)
    test_data_loader = neural_network.databunch.get_train_dataloader(
        batch_size=batch_size
    )

    neural_network.deserialize(path_to_model)

    # Evaluate model on test dataloader
    # mypy: as we are in the worker-side of the algorithm, we know that
    # _evaluate_local() will be the actual underlying call, and that that returns
    # EvaluateReturnType
    # TODO: [BIT-1604] Remove this cast statement once they become superfluous.
    eval_output: EvaluateReturnType = cast(
        EvaluateReturnType, neural_network.evaluate(test_data_loader)
    )
    preds = eval_output.preds
    targs = eval_output.targs

    metrics = MetricCollection.create_from_model(neural_network)
    results = metrics.compute(targs, preds)
    logging.info(str(results))


if __name__ == "__main__":
    fire.Fire(evaluate_model)
