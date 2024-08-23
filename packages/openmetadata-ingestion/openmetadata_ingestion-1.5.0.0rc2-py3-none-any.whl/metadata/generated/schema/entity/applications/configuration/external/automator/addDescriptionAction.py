# generated by datamodel-codegen:
#   filename:  entity/applications/configuration/external/automator/addDescriptionAction.json
#   timestamp: 2024-08-22T13:36:48+00:00

from __future__ import annotations

from enum import Enum
from typing import List, Optional

from pydantic import ConfigDict, Field
from typing_extensions import Annotated

from metadata.ingestion.models.custom_pydantic import BaseModel

from ......type import basic


class AddDescriptionActionType(Enum):
    AddDescriptionAction = 'AddDescriptionAction'


class AddDescriptionAction(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    type: Annotated[
        AddDescriptionActionType,
        Field(description='Application Type', title='Application Type'),
    ]
    description: Annotated[str, Field(description='Description to apply')]
    applyToChildren: Annotated[
        Optional[List[basic.EntityName]],
        Field(
            None,
            description='Apply the description to the children of the selected assets that match the criteria. E.g., columns, tasks, topic fields,...',
            title='Apply to Children',
        ),
    ]
    overwriteMetadata: Annotated[
        Optional[bool],
        Field(
            False,
            description="Update the description even if they are already defined in the asset. By default, we'll only add the descriptions to assets without the description set.",
            title='Overwrite Metadata',
        ),
    ]
