# generated by datamodel-codegen:
#   filename:  type/entityRelationship.json
#   timestamp: 2024-08-22T13:36:48+00:00

from __future__ import annotations

from enum import Enum
from typing import Optional

from pydantic import ConfigDict, Field
from typing_extensions import Annotated

from metadata.ingestion.models.custom_pydantic import BaseModel

from . import basic


class RelationshipType(Enum):
    contains = 'contains'
    createdBy = 'createdBy'
    repliedTo = 'repliedTo'
    isAbout = 'isAbout'
    addressedTo = 'addressedTo'
    mentionedIn = 'mentionedIn'
    testedBy = 'testedBy'
    uses = 'uses'
    owns = 'owns'
    parentOf = 'parentOf'
    has = 'has'
    follows = 'follows'
    joinedWith = 'joinedWith'
    upstream = 'upstream'
    appliedTo = 'appliedTo'
    relatedTo = 'relatedTo'
    reviews = 'reviews'
    reactedTo = 'reactedTo'
    voted = 'voted'
    expert = 'expert'
    editedBy = 'editedBy'
    defaultsTo = 'defaultsTo'


class EntityRelationship(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    fromId: Annotated[
        Optional[basic.Uuid],
        Field(
            None,
            description='Unique identifier that identifies the entity from which the relationship originates.',
        ),
    ]
    fromFQN: Annotated[
        Optional[str],
        Field(
            None,
            description='Fully qualified name of the entity from which the relationship originates.',
        ),
    ]
    fromEntity: Annotated[
        str,
        Field(
            description='Type of the entity from which the relationship originates. Examples: `database`, `table`, `metrics` ...'
        ),
    ]
    toId: Annotated[
        Optional[basic.Uuid],
        Field(
            None,
            description='Unique identifier that identifies the entity towards which the relationship refers to.',
        ),
    ]
    toFQN: Annotated[
        Optional[str],
        Field(
            None,
            description='Fully qualified name of the entity towards which the relationship refers to.',
        ),
    ]
    toEntity: Annotated[
        str,
        Field(
            description='Type of the entity towards which the relationship refers to. Examples: `database`, `table`, `metrics` ...'
        ),
    ]
    relation: Annotated[
        Optional[int],
        Field(
            None,
            description='Describes relationship between the two entities as an integer.',
            ge=0,
        ),
    ]
    relationshipType: Annotated[
        RelationshipType,
        Field(
            description='Describes relationship between the two entities. Eg: Database --- Contains --> Table.'
        ),
    ]
    deleted: Annotated[
        Optional[bool],
        Field(
            False,
            description='`true` indicates the relationship has been soft deleted.',
        ),
    ]
