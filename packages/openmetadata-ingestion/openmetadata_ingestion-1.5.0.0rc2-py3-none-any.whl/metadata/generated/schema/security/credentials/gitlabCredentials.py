# generated by datamodel-codegen:
#   filename:  security/credentials/gitlabCredentials.json
#   timestamp: 2024-08-22T13:36:48+00:00

from __future__ import annotations

from enum import Enum
from typing import Optional

from pydantic import ConfigDict, Field
from typing_extensions import Annotated

from metadata.ingestion.models.custom_pydantic import BaseModel

from . import gitCredentials


class GitlabType(Enum):
    Gitlab = 'Gitlab'


class GitlabCredentials(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    type: Annotated[
        Optional[GitlabType],
        Field(
            GitlabType.Gitlab, description='Credentials Type', title='Credentials Type'
        ),
    ]
    repositoryOwner: gitCredentials.RepositoryOwner
    repositoryName: gitCredentials.RepositoryName
    token: Optional[gitCredentials.Token] = None
