# generated by datamodel-codegen:
#   filename:  entity/services/connections/search/elasticSearch/basicAuth.json
#   timestamp: 2024-08-22T13:36:48+00:00

from __future__ import annotations

from typing import Optional

from pydantic import ConfigDict, Field
from typing_extensions import Annotated

from metadata.ingestion.models.custom_pydantic import BaseModel, CustomSecretStr


class BasicAuthentication(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    username: Annotated[
        Optional[str],
        Field(None, description='Elastic Search Username for Login', title='Username'),
    ]
    password: Annotated[
        Optional[CustomSecretStr],
        Field(None, description='Elastic Search Password for Login', title='Password'),
    ]
