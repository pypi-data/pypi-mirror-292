# generated by datamodel-codegen:
#   filename:  entity/applications/configuration/external/automator/removeDomainAction.json
#   timestamp: 2024-08-22T13:36:48+00:00

from __future__ import annotations

from enum import Enum

from pydantic import ConfigDict, Field
from typing_extensions import Annotated

from metadata.ingestion.models.custom_pydantic import BaseModel


class RemoveDomainActionType(Enum):
    RemoveDomainAction = 'RemoveDomainAction'


class RemoveDomainAction(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    type: Annotated[
        RemoveDomainActionType,
        Field(description='Application Type', title='Application Type'),
    ]
