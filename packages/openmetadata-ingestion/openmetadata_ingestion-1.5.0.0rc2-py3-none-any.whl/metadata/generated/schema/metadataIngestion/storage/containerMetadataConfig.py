# generated by datamodel-codegen:
#   filename:  metadataIngestion/storage/containerMetadataConfig.json
#   timestamp: 2024-08-22T13:36:48+00:00

from __future__ import annotations

from typing import List, Optional

from pydantic import ConfigDict, Field
from typing_extensions import Annotated

from metadata.ingestion.models.custom_pydantic import BaseModel

from ...entity.data import table


class MetadataEntry(BaseModel):
    dataPath: Annotated[
        str,
        Field(
            description='The path where the data resides in the container, excluding the bucket name',
            title='Data path',
        ),
    ]
    structureFormat: Annotated[
        Optional[str],
        Field(
            None,
            description="What's the schema format for the container, eg. avro, parquet, csv.",
            title='Schema format',
        ),
    ]
    unstructuredFormats: Annotated[
        Optional[List[str]],
        Field(
            None,
            description='What the unstructured formats you want to ingest, eg. png, pdf, jpg.',
            title='Unstructured format',
        ),
    ]
    separator: Annotated[
        Optional[str],
        Field(
            None,
            description='For delimited files such as CSV, what is the separator being used?',
            title='Separator',
        ),
    ]
    isPartitioned: Annotated[
        Optional[bool],
        Field(
            False,
            description="Flag indicating whether the container's data is partitioned",
            title='Is Partitioned',
        ),
    ]
    partitionColumns: Annotated[
        Optional[List[table.Column]],
        Field(
            None,
            description="What are the partition columns in case the container's data is partitioned",
            title='Partition Columns',
        ),
    ]


class StorageContainerConfig(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    entries: Annotated[
        List[MetadataEntry],
        Field(
            description='List of metadata entries for the bucket containing information about where data resides and its structure'
        ),
    ]
