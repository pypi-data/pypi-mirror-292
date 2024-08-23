# generated by datamodel-codegen:
#   filename:  auth/revokePersonalToken.json
#   timestamp: 2024-08-22T13:36:48+00:00

from __future__ import annotations

from typing import List, Optional

from pydantic import ConfigDict, Field
from typing_extensions import Annotated

from metadata.ingestion.models.custom_pydantic import BaseModel

from ..type import basic


class RevokePersonalToken(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    tokenIds: Annotated[
        Optional[List[basic.Uuid]],
        Field(None, description='Ids of Personal Access Tokens to remove.'),
    ]
