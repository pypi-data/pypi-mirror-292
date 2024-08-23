# generated by datamodel-codegen:
#   filename:  entity/applications/configuration/internal/searchIndexingAppConfig.json
#   timestamp: 2024-08-22T13:36:48+00:00

from __future__ import annotations

from enum import Enum
from typing import List, Optional

from pydantic import ConfigDict, Field
from typing_extensions import Annotated

from metadata.ingestion.models.custom_pydantic import BaseModel

from .....configuration import elasticSearchConfiguration


class SearchIndexingType(Enum):
    SearchIndexing = 'SearchIndexing'


class SearchIndexingApp(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    type: Annotated[
        Optional[SearchIndexingType],
        Field(
            SearchIndexingType.SearchIndexing,
            description='Application Type',
            title='Application Type',
        ),
    ]
    entities: Annotated[
        Optional[List[str]], Field(['all'], description='List of Entities to Reindex')
    ]
    recreateIndex: Annotated[
        Optional[bool], Field(False, description='This schema publisher run modes.')
    ]
    batchSize: Annotated[
        Optional[int],
        Field(
            100, description='Maximum number of events sent in a batch (Default 100).'
        ),
    ]
    searchIndexMappingLanguage: Annotated[
        Optional[elasticSearchConfiguration.SearchIndexMappingLanguage],
        Field(
            elasticSearchConfiguration.SearchIndexMappingLanguage.EN,
            description='Recreate Indexes with updated Language',
        ),
    ]
