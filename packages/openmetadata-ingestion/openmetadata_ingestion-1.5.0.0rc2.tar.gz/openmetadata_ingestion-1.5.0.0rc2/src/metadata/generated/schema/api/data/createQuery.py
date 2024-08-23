# generated by datamodel-codegen:
#   filename:  api/data/createQuery.json
#   timestamp: 2024-08-22T13:36:48+00:00

from __future__ import annotations

from typing import List, Optional

from pydantic import ConfigDict, Field
from typing_extensions import Annotated

from metadata.ingestion.models.custom_pydantic import BaseModel

from ...type import basic, entityReference, entityReferenceList, tagLabel


class CreateQueryRequest(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    name: Annotated[
        Optional[basic.EntityName],
        Field(None, description='Name of a Query in case of User Creation.'),
    ]
    displayName: Annotated[
        Optional[str],
        Field(None, description='Display Name that identifies this query.'),
    ]
    description: Annotated[
        Optional[basic.Markdown],
        Field(None, description='Description of the query instance.'),
    ]
    owners: Annotated[
        Optional[entityReferenceList.EntityReferenceList],
        Field(None, description='Owners of this entity'),
    ]
    tags: Annotated[
        Optional[List[tagLabel.TagLabel]],
        Field(None, description='Tags for this Query'),
    ]
    query: Annotated[basic.SqlQuery, Field(description='SQL Query definition.')]
    query_type: Annotated[Optional[str], Field(None, description='SQL query type')]
    exclude_usage: Annotated[
        Optional[bool],
        Field(
            None,
            description='Flag to check if query is to be excluded while processing usage',
        ),
    ]
    duration: Annotated[
        Optional[float],
        Field(None, description='How long did the query took to run in milliseconds.'),
    ]
    users: Annotated[
        Optional[List[basic.FullyQualifiedEntityName]],
        Field(None, description='UserName of the user running the query.'),
    ]
    usedBy: Annotated[
        Optional[List[str]],
        Field(
            None,
            description='List of users who ran the query but does not exist in OpenMetadata.',
        ),
    ]
    queryDate: Annotated[
        Optional[basic.Timestamp],
        Field(None, description='Date on which the query ran.'),
    ]
    queryUsedIn: Annotated[
        Optional[entityReferenceList.EntityReferenceList],
        Field(None, description='list of entities to which the query is joined.'),
    ]
    triggeredBy: Annotated[
        Optional[entityReference.EntityReference],
        Field(
            None,
            description='Entity that triggered the query. E.g., a Stored Procedure or a Pipeline Task.',
        ),
    ]
    processedLineage: Annotated[
        Optional[bool],
        Field(
            False,
            description='Flag if this query has already been successfully processed for lineage',
        ),
    ]
    service: Annotated[
        basic.FullyQualifiedEntityName,
        Field(
            description='Link to the database service fully qualified name where this query has been run'
        ),
    ]
    domain: Annotated[
        Optional[str],
        Field(
            None, description='Fully qualified name of the domain the Table belongs to.'
        ),
    ]
