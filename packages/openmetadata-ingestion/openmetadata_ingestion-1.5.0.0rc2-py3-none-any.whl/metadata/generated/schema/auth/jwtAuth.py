# generated by datamodel-codegen:
#   filename:  auth/jwtAuth.json
#   timestamp: 2024-08-22T13:36:48+00:00

from __future__ import annotations

from enum import Enum
from typing import Optional

from pydantic import ConfigDict, Field
from typing_extensions import Annotated

from metadata.ingestion.models.custom_pydantic import BaseModel, CustomSecretStr

from ..type import basic


class JWTTokenExpiry(Enum):
    OneHour = 'OneHour'
    field_1 = '1'
    field_7 = '7'
    field_30 = '30'
    field_60 = '60'
    field_90 = '90'
    Unlimited = 'Unlimited'


class JWTAuthMechanism(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    JWTToken: Annotated[
        CustomSecretStr, Field(description='JWT Auth Token.', title='JWT Token')
    ]
    JWTTokenExpiry: JWTTokenExpiry
    JWTTokenExpiresAt: Annotated[
        Optional[basic.Timestamp],
        Field(None, description='JWT Auth Token expiration time.'),
    ]
