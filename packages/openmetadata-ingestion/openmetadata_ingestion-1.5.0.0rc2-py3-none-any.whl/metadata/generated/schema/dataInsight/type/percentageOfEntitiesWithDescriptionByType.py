# generated by datamodel-codegen:
#   filename:  dataInsight/type/percentageOfEntitiesWithDescriptionByType.json
#   timestamp: 2024-08-22T13:36:48+00:00

from __future__ import annotations

from typing import Optional

from pydantic import ConfigDict, Field
from typing_extensions import Annotated

from metadata.ingestion.models.custom_pydantic import BaseModel

from ...type import basic


class PercentageOfEntitiesWithDescriptionByType(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    timestamp: Annotated[
        Optional[basic.Timestamp], Field(None, description='timestamp')
    ]
    entityType: Annotated[
        Optional[str],
        Field(None, description='Type of entity. Derived from the entity class.'),
    ]
    completedDescriptionFraction: Annotated[
        Optional[float],
        Field(
            None,
            description='decimal fraction of entity with completed description',
            ge=0.0,
            le=1.0,
        ),
    ]
    completedDescription: Annotated[
        Optional[float],
        Field(
            None, description='decimal fraction of entity with completed description'
        ),
    ]
    entityCount: Annotated[
        Optional[float],
        Field(
            None, description='decimal fraction of entity with completed description'
        ),
    ]
