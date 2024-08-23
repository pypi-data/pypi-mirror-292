# generated by datamodel-codegen:
#   filename:  entity/utils/supersetApiConnection.json
#   timestamp: 2024-08-22T13:36:48+00:00

from __future__ import annotations

from enum import Enum
from typing import Optional

from pydantic import ConfigDict, Field
from typing_extensions import Annotated

from metadata.ingestion.models.custom_pydantic import BaseModel, CustomSecretStr

from ...security.ssl import verifySSLConfig


class ApiProvider(Enum):
    db = 'db'
    ldap = 'ldap'


class SupersetApiConnection(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    provider: Annotated[
        ApiProvider,
        Field(
            description="Authentication provider for the Superset service. For basic user/password authentication, the default value `db` can be used. This parameter is used internally to connect to Superset's REST API.",
            title='Provider',
        ),
    ]
    username: Annotated[
        str, Field(description='Username for Superset.', title='Username')
    ]
    password: Annotated[
        CustomSecretStr, Field(description='Password for Superset.', title='Password')
    ]
    verifySSL: Optional[verifySSLConfig.VerifySSL] = verifySSLConfig.VerifySSL.no_ssl
    sslConfig: Optional[verifySSLConfig.SslConfig] = None
