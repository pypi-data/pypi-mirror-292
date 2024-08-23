# generated by datamodel-codegen:
#   filename:  type/votes.json
#   timestamp: 2024-08-22T13:36:48+00:00

from __future__ import annotations

from enum import Enum
from typing import Optional

from pydantic import ConfigDict, Field
from typing_extensions import Annotated

from metadata.ingestion.models.custom_pydantic import BaseModel

from . import entityReferenceList


class Votes(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    upVotes: Annotated[
        Optional[int], Field(0, description='Total up-votes the entity has')
    ]
    downVotes: Annotated[
        Optional[int], Field(0, description='Total down-votes the entity has')
    ]
    upVoters: Annotated[
        Optional[entityReferenceList.EntityReferenceList],
        Field(None, description='List of all the Users who upVoted'),
    ]
    downVoters: Annotated[
        Optional[entityReferenceList.EntityReferenceList],
        Field(None, description='List of all the Users who downVoted'),
    ]


class VoteType(Enum):
    votedUp = 'votedUp'
    votedDown = 'votedDown'
    unVoted = 'unVoted'
