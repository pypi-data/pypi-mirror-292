# generated by datamodel-codegen:
#   filename:  entity/services/storageService.json
#   timestamp: 2024-08-22T13:36:48+00:00

from __future__ import annotations

from enum import Enum
from typing import List, Optional, Union

from pydantic import ConfigDict, Field
from typing_extensions import Annotated

from metadata.ingestion.models.custom_pydantic import BaseModel

from ...type import basic, entityHistory, entityReference, entityReferenceList, tagLabel
from .connections import testConnectionResult
from .connections.storage import (
    adlsConnection,
    customStorageConnection,
    gcsConnection,
    s3Connection,
)


class StorageServiceType(Enum):
    S3 = 'S3'
    ADLS = 'ADLS'
    GCS = 'GCS'
    CustomStorage = 'CustomStorage'


class StorageConnection(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    config: Optional[
        Union[
            s3Connection.S3Connection,
            adlsConnection.AdlsConnection,
            gcsConnection.GcsConnection,
            customStorageConnection.CustomStorageConnection,
        ]
    ] = None


class StorageService(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    id: Annotated[
        basic.Uuid,
        Field(description='Unique identifier of this storage service instance.'),
    ]
    name: Annotated[
        basic.EntityName,
        Field(description='Name that identifies this storage service.'),
    ]
    fullyQualifiedName: Annotated[
        Optional[basic.FullyQualifiedEntityName],
        Field(None, description='FullyQualifiedName same as `name`.'),
    ]
    displayName: Annotated[
        Optional[str],
        Field(None, description='Display Name that identifies this storage service.'),
    ]
    serviceType: Annotated[
        StorageServiceType,
        Field(description='Type of storage service such as S3, GCS, AZURE...'),
    ]
    description: Annotated[
        Optional[basic.Markdown],
        Field(None, description='Description of a storage service instance.'),
    ]
    connection: Optional[StorageConnection] = None
    pipelines: Annotated[
        Optional[entityReferenceList.EntityReferenceList],
        Field(
            None,
            description='References to pipelines deployed for this storage service to extract metadata, usage, lineage etc..',
        ),
    ]
    testConnectionResult: Annotated[
        Optional[testConnectionResult.TestConnectionResult],
        Field(None, description='Last test connection results for this service'),
    ]
    tags: Annotated[
        Optional[List[tagLabel.TagLabel]],
        Field(None, description='Tags for this storage Service.'),
    ]
    version: Annotated[
        Optional[entityHistory.EntityVersion],
        Field(None, description='Metadata version of the entity.'),
    ]
    updatedAt: Annotated[
        Optional[basic.Timestamp],
        Field(
            None,
            description='Last update time corresponding to the new version of the entity in Unix epoch time milliseconds.',
        ),
    ]
    updatedBy: Annotated[
        Optional[str], Field(None, description='User who made the update.')
    ]
    href: Annotated[
        Optional[basic.Href],
        Field(
            None,
            description='Link to the resource corresponding to this storage service.',
        ),
    ]
    owners: Annotated[
        Optional[entityReferenceList.EntityReferenceList],
        Field(None, description='Owners of this storage service.'),
    ]
    changeDescription: Annotated[
        Optional[entityHistory.ChangeDescription],
        Field(None, description='Change that lead to this version of the entity.'),
    ]
    deleted: Annotated[
        Optional[bool],
        Field(
            False, description='When `true` indicates the entity has been soft deleted.'
        ),
    ]
    dataProducts: Annotated[
        Optional[entityReferenceList.EntityReferenceList],
        Field(None, description='List of data products this entity is part of.'),
    ]
    domain: Annotated[
        Optional[entityReference.EntityReference],
        Field(None, description='Domain the Storage service belongs to.'),
    ]
