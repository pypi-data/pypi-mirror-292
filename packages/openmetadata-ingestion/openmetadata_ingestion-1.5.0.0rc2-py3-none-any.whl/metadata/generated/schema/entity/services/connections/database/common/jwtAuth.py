# generated by datamodel-codegen:
#   filename:  entity/services/connections/database/common/jwtAuth.json
#   timestamp: 2024-08-22T13:36:48+00:00

from __future__ import annotations

from typing import Optional

from pydantic import ConfigDict, Field
from typing_extensions import Annotated

from metadata.ingestion.models.custom_pydantic import BaseModel, CustomSecretStr


class JwtAuth(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    jwt: Annotated[
        Optional[CustomSecretStr],
        Field(None, description='JWT to connect to source.', title='JWT'),
    ]
