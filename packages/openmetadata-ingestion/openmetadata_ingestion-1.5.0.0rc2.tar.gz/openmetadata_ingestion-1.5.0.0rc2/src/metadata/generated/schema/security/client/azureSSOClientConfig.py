# generated by datamodel-codegen:
#   filename:  security/client/azureSSOClientConfig.json
#   timestamp: 2024-08-22T13:36:48+00:00

from __future__ import annotations

from typing import List

from pydantic import ConfigDict, Field
from typing_extensions import Annotated

from metadata.ingestion.models.custom_pydantic import BaseModel, CustomSecretStr


class AzureSSOClientConfig(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    clientSecret: Annotated[
        CustomSecretStr, Field(description='Azure SSO client secret key')
    ]
    authority: Annotated[str, Field(description='Azure SSO Authority')]
    clientId: Annotated[str, Field(description='Azure Client ID.')]
    scopes: Annotated[List[str], Field(description='Azure Client ID.')]
