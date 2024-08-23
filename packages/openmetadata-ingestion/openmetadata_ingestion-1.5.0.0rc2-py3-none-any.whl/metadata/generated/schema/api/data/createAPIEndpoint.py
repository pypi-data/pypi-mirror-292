# generated by datamodel-codegen:
#   filename:  api/data/createAPIEndpoint.json
#   timestamp: 2024-08-22T13:36:48+00:00

from __future__ import annotations

from typing import List, Optional

from pydantic import AnyUrl, ConfigDict, Field
from typing_extensions import Annotated

from metadata.ingestion.models.custom_pydantic import BaseModel

from ...entity.data import apiEndpoint
from ...type import apiSchema, basic, entityReferenceList, lifeCycle, tagLabel


class CreateAPIEndpointRequest(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    name: Annotated[
        basic.EntityName,
        Field(
            description='Name that identifies this APIEndpoint instance uniquely. We use operationId from OpenAPI specification.'
        ),
    ]
    displayName: Annotated[
        Optional[str],
        Field(None, description='Display Name that identifies this APIEndpoint.'),
    ]
    description: Annotated[
        Optional[basic.Markdown],
        Field(
            None,
            description='Description of the APIEndpoint instance. What it has and how to use it.',
        ),
    ]
    apiCollection: Annotated[
        basic.FullyQualifiedEntityName,
        Field(
            description='Reference to API Collection that contains this API Endpoint.'
        ),
    ]
    endpointURL: Annotated[
        AnyUrl,
        Field(
            description='EndPoint URL for the API Collection. Capture the Root URL of the collection.',
            title='Endpoint URL',
        ),
    ]
    requestMethod: Annotated[
        Optional[apiEndpoint.ApiRequestMethod],
        Field(
            apiEndpoint.ApiRequestMethod.GET,
            description='Request Method for the API Endpoint.',
        ),
    ]
    requestSchema: Annotated[
        Optional[apiSchema.APISchema],
        Field(None, description='Request Schema for the API Endpoint.'),
    ]
    responseSchema: Annotated[
        Optional[apiSchema.APISchema],
        Field(None, description='Response Schema for the API Endpoint.'),
    ]
    owners: Annotated[
        Optional[entityReferenceList.EntityReferenceList],
        Field(None, description='Owners of this topic'),
    ]
    tags: Annotated[
        Optional[List[tagLabel.TagLabel]],
        Field(None, description='Tags for this topic'),
    ]
    extension: Annotated[
        Optional[basic.EntityExtension],
        Field(
            None,
            description='Entity extension data with custom attributes added to the entity.',
        ),
    ]
    sourceUrl: Annotated[
        Optional[basic.SourceUrl], Field(None, description='Source URL of topic.')
    ]
    domain: Annotated[
        Optional[basic.FullyQualifiedEntityName],
        Field(
            None, description='Fully qualified name of the domain the API belongs to.'
        ),
    ]
    dataProducts: Annotated[
        Optional[List[basic.FullyQualifiedEntityName]],
        Field(
            None,
            description='List of fully qualified names of data products this entity is part of.',
        ),
    ]
    lifeCycle: Annotated[
        Optional[lifeCycle.LifeCycle],
        Field(None, description='Life Cycle of the entity'),
    ]
    sourceHash: Annotated[
        Optional[str],
        Field(
            None, description='Source hash of the entity', max_length=32, min_length=1
        ),
    ]
