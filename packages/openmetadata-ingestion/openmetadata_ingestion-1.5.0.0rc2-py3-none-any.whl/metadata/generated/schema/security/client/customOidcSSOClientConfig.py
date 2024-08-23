# generated by datamodel-codegen:
#   filename:  security/client/customOidcSSOClientConfig.json
#   timestamp: 2024-08-22T13:36:48+00:00

from __future__ import annotations

from pydantic import ConfigDict, Field
from typing_extensions import Annotated

from metadata.ingestion.models.custom_pydantic import BaseModel, CustomSecretStr


class CustomOIDCSSOClientConfig(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    clientId: Annotated[str, Field(description='Custom OIDC Client ID.')]
    secretKey: Annotated[
        CustomSecretStr, Field(description='Custom OIDC Client Secret Key.')
    ]
    tokenEndpoint: Annotated[str, Field(description='Custom OIDC token endpoint.')]
