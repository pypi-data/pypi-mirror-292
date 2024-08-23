# generated by datamodel-codegen:
#   filename:  entity/services/connections/database/sapHana/sapHanaHDBConnection.json
#   timestamp: 2024-08-22T13:36:48+00:00

from __future__ import annotations

from typing import Optional

from pydantic import ConfigDict, Field
from typing_extensions import Annotated

from metadata.ingestion.models.custom_pydantic import BaseModel


class SapHanaHDBConnection(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    userKey: Annotated[
        Optional[str],
        Field(
            None,
            description='HDB Store User Key generated from the command `hdbuserstore SET <KEY> <host:port> <USERNAME> <PASSWORD>`',
            title='User Key',
        ),
    ]
