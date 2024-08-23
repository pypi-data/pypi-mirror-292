# generated by datamodel-codegen:
#   filename:  metadataIngestion/storage/storageMetadataGCSConfig.json
#   timestamp: 2024-08-22T13:36:48+00:00

from __future__ import annotations

from typing import Optional

from pydantic import ConfigDict, Field
from typing_extensions import Annotated

from metadata.ingestion.models.custom_pydantic import BaseModel

from ...security.credentials import gcpCredentials
from . import storageBucketDetails


class StorageMetadataGcsConfig(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    securityConfig: Annotated[
        Optional[gcpCredentials.GCPCredentials],
        Field(None, title='GCS Security Config'),
    ]
    prefixConfig: Annotated[
        storageBucketDetails.StorageMetadataBucketDetails,
        Field(title='Storage Metadata Prefix Config'),
    ]
