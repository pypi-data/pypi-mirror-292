# generated by datamodel-codegen:
#   filename:  entity/applications/configuration/external/metaPilotAppConfig.json
#   timestamp: 2024-08-22T13:36:48+00:00

from __future__ import annotations

from enum import Enum
from typing import List, Optional

from pydantic import ConfigDict, Field
from typing_extensions import Annotated

from metadata.ingestion.models.custom_pydantic import BaseModel

from .....type import entityReference


class MetaPilotAppType(Enum):
    MetaPilot = 'MetaPilot'


class MetaPilotAppConfig(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    type: Annotated[
        Optional[MetaPilotAppType],
        Field(
            MetaPilotAppType.MetaPilot,
            description='Application Type',
            title='Application Type',
        ),
    ]
    descriptionDatabases: Annotated[
        Optional[List[entityReference.EntityReference]],
        Field(
            None,
            description='Services and Databases configured to get the descriptions from.',
            title='Databases for Automated Description Generation',
        ),
    ]
    patchIfEmpty: Annotated[
        Optional[bool],
        Field(
            False,
            description='Patch the description if it is empty, instead of raising a suggestion',
            title='Patch Description If Empty',
        ),
    ]
    copilotDatabases: Annotated[
        Optional[List[entityReference.EntityReference]],
        Field(
            None,
            description='Services and Databases configured to get enable the SQL Copilot.',
            title='Databases for SQL Copilot',
        ),
    ]
    defaultScope: Annotated[
        Optional[entityReference.EntityReference],
        Field(
            None,
            description='Default database scope for the chatbot.',
            title='Default Chatbot Database Scope',
        ),
    ]
