# generated by datamodel-codegen:
#   filename:  configuration/jwtTokenConfiguration.json
#   timestamp: 2024-08-22T13:36:48+00:00

from __future__ import annotations

from typing import Optional

from pydantic import ConfigDict, Field
from typing_extensions import Annotated

from metadata.ingestion.models.custom_pydantic import BaseModel


class JWTTokenConfiguration(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    rsapublicKeyFilePath: Annotated[
        Optional[str], Field(None, description='RSA Public Key File Path')
    ]
    rsaprivateKeyFilePath: Annotated[
        Optional[str], Field(None, description='RSA Private Key File Path')
    ]
    jwtissuer: Annotated[str, Field(description='JWT Issuer')]
    keyId: Annotated[str, Field(description='Key ID')]
