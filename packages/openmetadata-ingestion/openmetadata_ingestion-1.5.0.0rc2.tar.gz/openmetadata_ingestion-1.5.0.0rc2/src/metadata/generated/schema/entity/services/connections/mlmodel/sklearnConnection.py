# generated by datamodel-codegen:
#   filename:  entity/services/connections/mlmodel/sklearnConnection.json
#   timestamp: 2024-08-22T13:36:48+00:00

from __future__ import annotations

from enum import Enum
from typing import Optional

from pydantic import ConfigDict, Field
from typing_extensions import Annotated

from metadata.ingestion.models.custom_pydantic import BaseModel

from .. import connectionBasicType


class SklearnType(Enum):
    Sklearn = 'Sklearn'


class SklearnConnection(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    type: Annotated[
        Optional[SklearnType],
        Field(SklearnType.Sklearn, description='Service Type', title='Service Type'),
    ]
    supportsMetadataExtraction: Annotated[
        Optional[connectionBasicType.SupportsMetadataExtraction],
        Field(None, title='Supports Metadata Extraction'),
    ]
