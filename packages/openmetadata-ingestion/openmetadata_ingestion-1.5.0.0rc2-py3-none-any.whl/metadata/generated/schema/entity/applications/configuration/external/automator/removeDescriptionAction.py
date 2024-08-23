# generated by datamodel-codegen:
#   filename:  entity/applications/configuration/external/automator/removeDescriptionAction.json
#   timestamp: 2024-08-22T13:36:48+00:00

from __future__ import annotations

from enum import Enum
from typing import List, Optional

from pydantic import ConfigDict, Field
from typing_extensions import Annotated

from metadata.ingestion.models.custom_pydantic import BaseModel

from ......type import basic


class RemoveDescriptionActionType(Enum):
    RemoveDescriptionAction = 'RemoveDescriptionAction'


class RemoveDescriptionAction(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    type: Annotated[
        RemoveDescriptionActionType,
        Field(description='Application Type', title='Application Type'),
    ]
    applyToChildren: Annotated[
        Optional[List[basic.EntityName]],
        Field(
            None,
            description='Remove descriptions from all children of the selected assets. E.g., columns, tasks, topic fields,...',
            title='Apply to Children',
        ),
    ]
