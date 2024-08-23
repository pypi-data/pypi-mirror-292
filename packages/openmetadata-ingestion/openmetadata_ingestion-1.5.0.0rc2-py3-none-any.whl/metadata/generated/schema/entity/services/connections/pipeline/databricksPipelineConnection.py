# generated by datamodel-codegen:
#   filename:  entity/services/connections/pipeline/databricksPipelineConnection.json
#   timestamp: 2024-08-22T13:36:48+00:00

from __future__ import annotations

from enum import Enum
from typing import Optional

from pydantic import ConfigDict, Field
from typing_extensions import Annotated

from metadata.ingestion.models.custom_pydantic import BaseModel, CustomSecretStr

from .. import connectionBasicType


class DatabricksType(Enum):
    DatabricksPipeline = 'DatabricksPipeline'


class DatabricksPipelineConnection(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    type: Annotated[
        Optional[DatabricksType],
        Field(
            DatabricksType.DatabricksPipeline,
            description='Service Type',
            title='Service Type',
        ),
    ]
    hostPort: Annotated[
        str,
        Field(
            description='Host and port of the Databricks service.',
            title='Host and Port',
        ),
    ]
    token: Annotated[
        CustomSecretStr,
        Field(description='Generated Token to connect to Databricks.', title='Token'),
    ]
    httpPath: Annotated[
        Optional[str],
        Field(None, description='Databricks compute resources URL.', title='Http Path'),
    ]
    connectionArguments: Annotated[
        Optional[connectionBasicType.ConnectionArguments],
        Field(None, title='Connection Arguments'),
    ]
    supportsMetadataExtraction: Annotated[
        Optional[connectionBasicType.SupportsMetadataExtraction],
        Field(None, title='Supports Metadata Extraction'),
    ]
