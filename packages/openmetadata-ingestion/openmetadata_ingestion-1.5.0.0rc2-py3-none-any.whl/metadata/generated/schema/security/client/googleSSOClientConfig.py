# generated by datamodel-codegen:
#   filename:  security/client/googleSSOClientConfig.json
#   timestamp: 2024-08-22T13:36:48+00:00

from __future__ import annotations

from typing import Optional

from pydantic import ConfigDict, Field
from typing_extensions import Annotated

from metadata.ingestion.models.custom_pydantic import BaseModel, CustomSecretStr


class GoogleSSOClientConfig(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    secretKey: Annotated[
        CustomSecretStr,
        Field(description='Google SSO client secret key path or contents.'),
    ]
    audience: Annotated[
        Optional[str],
        Field(
            'https://www.googleapis.com/oauth2/v4/token',
            description='Google SSO audience URL',
        ),
    ]
