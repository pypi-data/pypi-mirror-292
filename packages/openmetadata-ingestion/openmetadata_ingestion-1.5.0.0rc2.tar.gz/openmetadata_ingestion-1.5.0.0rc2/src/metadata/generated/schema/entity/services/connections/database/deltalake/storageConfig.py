# generated by datamodel-codegen:
#   filename:  entity/services/connections/database/deltalake/storageConfig.json
#   timestamp: 2024-08-22T13:36:48+00:00

from __future__ import annotations

from typing import Optional

from pydantic import ConfigDict, Field
from typing_extensions import Annotated

from metadata.ingestion.models.custom_pydantic import BaseModel

from ..datalake import s3Config


class StorageConfig(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    connection: Annotated[
        s3Config.S3Config,
        Field(
            description='Available sources to fetch files.',
            title='DeltaLake Storage Configuration Source',
        ),
    ]
    bucketName: Annotated[
        Optional[str],
        Field('', description='Bucket Name of the data source.', title='Bucket Name'),
    ]
    prefix: Annotated[
        Optional[str],
        Field('', description='Prefix of the data source.', title='Prefix'),
    ]


class LocalConfig(BaseModel):
    pass
    model_config = ConfigDict(
        extra='forbid',
    )
