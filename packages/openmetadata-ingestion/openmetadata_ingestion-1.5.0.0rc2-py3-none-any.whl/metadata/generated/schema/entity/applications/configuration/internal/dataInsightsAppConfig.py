# generated by datamodel-codegen:
#   filename:  entity/applications/configuration/internal/dataInsightsAppConfig.json
#   timestamp: 2024-08-22T13:36:48+00:00

from __future__ import annotations

from datetime import date
from enum import Enum
from typing import Optional

from pydantic import ConfigDict, Field
from typing_extensions import Annotated

from metadata.ingestion.models.custom_pydantic import BaseModel


class DataInsightsAppType(Enum):
    DataInsights = 'DataInsights'


class BackfillConfiguration(BaseModel):
    enabled: Annotated[
        Optional[bool],
        Field(
            None,
            description='Enable Backfill for the configured dates',
            title='Enabled',
        ),
    ]
    startDate: Annotated[
        Optional[date],
        Field(
            None,
            description='Date from which to start the backfill',
            title='Start Date',
        ),
    ]
    endDate: Annotated[
        Optional[date],
        Field(
            None, description='Date for which the backfill will end', title='End Date'
        ),
    ]


class DataInsightsAppConfig(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    type: Annotated[
        Optional[DataInsightsAppType],
        Field(
            DataInsightsAppType.DataInsights,
            description='Application Type',
            title='Application Type',
        ),
    ]
    batchSize: Annotated[
        Optional[int],
        Field(
            100,
            description='Maximum number of events processed at a time (Default 100).',
        ),
    ]
    recreateDataAssetsIndex: Annotated[
        Optional[bool],
        Field(
            False,
            description='Recreates the DataAssets index on DataInsights. Useful if you changed a Custom Property Type and are facing errors. Bear in mind that recreating the index will delete your DataAssets and a backfill will be needed.',
            title='Recreate DataInsights DataAssets Index',
        ),
    ]
    backfillConfiguration: Optional[BackfillConfiguration] = None
