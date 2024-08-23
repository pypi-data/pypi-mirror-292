from typing import Any, Dict, Union

from DashAI.back.config_object import ConfigObject
from DashAI.back.core.schema_fields import (
    bool_field,
    none_type,
    schema_field,
    string_field,
)
from DashAI.back.core.schema_fields.base_schema import BaseSchema
from DashAI.back.dataloaders.classes.dataloader import (
    BaseDataLoader,
    DataloaderMoreOptionsSchema,
    DatasetSplitsSchema,
)
from datasets import DatasetDict, load_dataset  # Huggingface dataset library
from starlette.datastructures import UploadFile


class ExampleDataLoaderSchema(BaseSchema):
    """ GUI fields for the dataloader

    Suggested fields for a dataloader below
    """
    name: schema_field(
        none_type(string_field()),
        "",
        (
            "Custom name to register your dataset. If no name is specified, "
            "the name of the uploaded file will be used."
        ),
    )  # type: ignore
    splits_in_folders: schema_field(
        bool_field(),
        False,
        (
            "If your data has folders that define the splits select 'true', "
            "otherwise 'false'."
        ),
    )  # type: ignore
    splits: DatasetSplitsSchema  # train_size, test_size, val_size
    more_options: DataloaderMoreOptionsSchema  # shuffle, seed, stratify


class ExampleDataLoaderClass(BaseDataLoader, ConfigObject):
    """Load data from a directory."""

    COMPATIBLE_COMPONENTS = []
    SCHEMA = ExampleDataLoaderSchema

    def load_data(
        self,
        filepath_or_buffer: Union[UploadFile, str],
        temp_path: str,
        params: Dict[str, Any],
    ) -> DatasetDict:
        """Load a dataset.

        For more information visit: https://huggingface.co/docs/datasets/index

        Parameters
        ----------
        filepath_or_buffer : Union[UploadFile, str], optional
            An URL where the dataset is located or a FastAPI/Uvicorn uploaded file
            object.
        temp_path : str
            The temporary path where the files will be extracted and then uploaded.
        params : Dict[str, Any]
            Dict with the dataloader parameters.

        Returns
        -------
        DatasetDict
            A HuggingFace's Dataset with the loaded data.
        """
        raise NotImplementedError
