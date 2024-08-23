# generated by datamodel-codegen:
#   filename:  metadataIngestion/dbtconfig/dbtBucketDetails.json
#   timestamp: 2024-08-22T13:36:48+00:00

from __future__ import annotations

from typing import Optional

from pydantic import ConfigDict, Field
from typing_extensions import Annotated

from metadata.ingestion.models.custom_pydantic import BaseModel


class DbtBucketDetails(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    dbtBucketName: Annotated[
        Optional[str],
        Field(
            None,
            description='Name of the bucket where the dbt files are stored',
            title='DBT Bucket Name',
        ),
    ]
    dbtObjectPrefix: Annotated[
        Optional[str],
        Field(
            None,
            description='Path of the folder where the dbt files are stored',
            title='DBT Object Prefix',
        ),
    ]
