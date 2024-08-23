# generated by datamodel-codegen:
#   filename:  security/credentials/accessTokenAuth.json
#   timestamp: 2024-08-22T13:36:48+00:00

from __future__ import annotations

from pydantic import ConfigDict, Field
from typing_extensions import Annotated

from metadata.ingestion.models.custom_pydantic import BaseModel, CustomSecretStr


class AccessTokenAuth(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    personalAccessTokenName: Annotated[
        str,
        Field(description='Personal Access Token Name.', title='Personal Access Token'),
    ]
    personalAccessTokenSecret: Annotated[
        CustomSecretStr,
        Field(
            description='Personal Access Token Secret.',
            title='Personal Access Token Secret',
        ),
    ]
