import numpy as np

from DashAI.back.dataloaders.classes.dashai_dataset import DashAIDataset
from DashAI.back.metrics.base_metric import BaseMetric
from DashAI.back.core.schema_fields import BaseSchema, schema_field


class ExampleMetricSchema(BaseSchema):
    """ GUI fields for the metric"""
    example_param_name: schema_field(  # Change example_param_name
        type_field(), # Choose between different types_fields e.g. int_field, string_field, etc
        placeholder=, # Placeholde to display in UI
        description=(
            "Field description"
        ),
    )  # type: ignore


class ExampleMetricClass(BaseMetric):

    SCHEMA = ExampleMetricSchema
    COMPATIBLE_COMPONENTS = ["TaskName"]

    @staticmethod
    def score(true_labels: DashAIDataset, probs_pred_labels: np.ndarray) -> float:
        """Calculate recall between true labels and predicted labels.

        Parameters
        ----------
        true_labels : DashAIDataset
            A DashAI dataset with labels.
        probs_pred_labels :  np.ndarray
            A two-dimensional matrix in which each column represents a class and the row
            values represent the probability that an example belongs to the class
            associated with the column.

        Returns
        -------
        float
            recall score between true labels and predicted labels
        """
        raise NotImplementedError
