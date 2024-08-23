# generated by datamodel-codegen:
#   filename:  entity/data/query.json
#   timestamp: 2024-08-22T13:36:48+00:00

from __future__ import annotations

from typing import List, Optional

from pydantic import ConfigDict, Field
from typing_extensions import Annotated

from metadata.ingestion.models.custom_pydantic import BaseModel

from ...type import (
    basic,
    entityHistory,
    entityReference,
    entityReferenceList,
    tagLabel,
    votes,
)


class Query(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    id: Annotated[
        Optional[basic.Uuid], Field(None, description='Unique identifier of the query.')
    ]
    name: Annotated[
        basic.EntityName,
        Field(description='Name of an entity to which the query belongs to'),
    ]
    fullyQualifiedName: Annotated[
        Optional[basic.FullyQualifiedEntityName],
        Field(None, description='Fully qualified name of a query.'),
    ]
    displayName: Annotated[
        Optional[str],
        Field(
            None,
            description='Display Name that identifies this Query. It could be title or label.',
        ),
    ]
    description: Annotated[
        Optional[basic.Markdown], Field(None, description='Description of a query.')
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
        Optional[str], Field(None, description='User who made the query.')
    ]
    href: Annotated[
        Optional[basic.Href], Field(None, description='Link to this Query resource.')
    ]
    changeDescription: Annotated[
        Optional[entityHistory.ChangeDescription],
        Field(None, description='Change that lead to this version of the entity.'),
    ]
    owners: Annotated[
        Optional[entityReferenceList.EntityReferenceList],
        Field(None, description='Owners of this Query.'),
    ]
    duration: Annotated[
        Optional[float],
        Field(None, description='How long did the query took to run in milliseconds.'),
    ]
    users: Annotated[
        Optional[List[entityReference.EntityReference]],
        Field(None, description='List of users who ran this query.'),
    ]
    followers: Annotated[
        Optional[entityReferenceList.EntityReferenceList],
        Field(None, description='Followers of this Query.'),
    ]
    votes: Annotated[
        Optional[votes.Votes], Field(None, description='Votes on the entity.')
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
    checksum: Annotated[
        Optional[str],
        Field(None, description='Checksum to avoid registering duplicate queries.'),
    ]
    queryDate: Annotated[
        Optional[basic.Timestamp],
        Field(None, description='Date on which the query ran.'),
    ]
    usedBy: Annotated[
        Optional[List[str]],
        Field(
            None,
            description='List of users who ran the query but does not exist in OpenMetadata.',
        ),
    ]
    tags: Annotated[
        Optional[List[tagLabel.TagLabel]],
        Field(None, description='Tags for this SQL query.'),
    ]
    queryUsedIn: Annotated[
        Optional[entityReferenceList.EntityReferenceList],
        Field(None, description='Entities that are using this query'),
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
        entityReference.EntityReference,
        Field(description='Link to the service this query belongs to.'),
    ]
    domain: Annotated[
        Optional[entityReference.EntityReference],
        Field(
            None,
            description='Domain the asset belongs to. When not set, the asset inherits the domain from the parent it belongs to.',
        ),
    ]
