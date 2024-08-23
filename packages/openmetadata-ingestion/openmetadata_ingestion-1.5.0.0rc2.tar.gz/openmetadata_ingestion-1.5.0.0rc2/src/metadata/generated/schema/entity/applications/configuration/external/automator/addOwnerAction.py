# generated by datamodel-codegen:
#   filename:  entity/applications/configuration/external/automator/addOwnerAction.json
#   timestamp: 2024-08-22T13:36:48+00:00

from __future__ import annotations

from enum import Enum
from typing import Optional

from pydantic import ConfigDict, Field
from typing_extensions import Annotated

from metadata.ingestion.models.custom_pydantic import BaseModel

from ......type import entityReferenceList


class AddOwnerActionType(Enum):
    AddOwnerAction = 'AddOwnerAction'


class AddOwnerAction(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    type: Annotated[
        AddOwnerActionType,
        Field(description='Application Type', title='Application Type'),
    ]
    owners: Annotated[
        entityReferenceList.EntityReferenceList, Field(description='Owners to apply')
    ]
    overwriteMetadata: Annotated[
        Optional[bool],
        Field(
            False,
            description='Update the owners even if it is defined in the asset. By default, we will only apply the owners to assets without owner.',
            title='Overwrite Metadata',
        ),
    ]
