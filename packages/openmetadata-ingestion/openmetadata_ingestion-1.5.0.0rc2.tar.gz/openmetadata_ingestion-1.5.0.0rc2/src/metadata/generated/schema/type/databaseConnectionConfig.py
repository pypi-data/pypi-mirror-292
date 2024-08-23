# generated by datamodel-codegen:
#   filename:  type/databaseConnectionConfig.json
#   timestamp: 2024-08-22T13:36:48+00:00

from __future__ import annotations

from typing import List, Optional

from pydantic import ConfigDict, Field
from typing_extensions import Annotated

from metadata.ingestion.models.custom_pydantic import BaseModel


class DatabaseConnectionConfig(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    username: Annotated[
        Optional[str],
        Field(None, description='username to connect  to the data source.'),
    ]
    password: Annotated[
        Optional[str],
        Field(None, description='password to connect  to the data source.'),
    ]
    hostPort: Annotated[
        Optional[str], Field(None, description='Host and port of the data source.')
    ]
    database: Annotated[
        Optional[str], Field(None, description='Database of the data source.')
    ]
    schema_: Annotated[
        Optional[str],
        Field(None, alias='schema', description='schema of the data source.'),
    ]
    includeViews: Annotated[
        Optional[bool],
        Field(
            True,
            description='optional configuration to turn off fetching metadata for views.',
        ),
    ]
    includeTables: Annotated[
        Optional[bool],
        Field(
            True,
            description='Optional configuration to turn off fetching metadata for tables.',
        ),
    ]
    generateSampleData: Annotated[
        Optional[bool], Field(True, description='Turn on/off collecting sample data.')
    ]
    sampleDataQuery: Annotated[
        Optional[str],
        Field(
            'select * from {}.{} limit 50', description='query to generate sample data.'
        ),
    ]
    enableDataProfiler: Annotated[
        Optional[bool],
        Field(
            False,
            description='Run data profiler as part of ingestion to get table profile data.',
        ),
    ]
    includeFilterPattern: Annotated[
        Optional[List[str]],
        Field(
            None,
            description='Regex to only fetch tables or databases that matches the pattern.',
        ),
    ]
    excludeFilterPattern: Annotated[
        Optional[List[str]],
        Field(
            None,
            description='Regex exclude tables or databases that matches the pattern.',
        ),
    ]
