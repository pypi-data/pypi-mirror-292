# generated by datamodel-codegen:
#   filename:  dataInsight/custom/dataInsightCustomChart.json
#   timestamp: 2024-08-22T13:36:48+00:00

from __future__ import annotations

from enum import Enum
from typing import Optional, Union

from pydantic import ConfigDict, Field
from typing_extensions import Annotated

from metadata.ingestion.models.custom_pydantic import BaseModel

from ...type import basic, entityHistory, entityReference
from . import lineChart, summaryCard


class ChartType(Enum):
    LineChart = 'LineChart'
    AreaChart = 'AreaChart'
    BarChart = 'BarChart'
    SummaryCard = 'SummaryCard'


class Function(Enum):
    count = 'count'
    sum = 'sum'
    avg = 'avg'
    min = 'min'
    max = 'max'
    unique = 'unique'


class KpiDetails(BaseModel):
    startDate: Annotated[Optional[str], Field(None, description='Start Date of KPI')]
    endDate: Annotated[Optional[str], Field(None, description='End Date of KPI')]
    target: Annotated[Optional[float], Field(None, description='Target value of KPI')]


class Chart(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    id: Annotated[
        Optional[basic.Uuid],
        Field(None, description='Unique identifier of this table instance.'),
    ]
    name: Annotated[
        basic.EntityName,
        Field(description='Name that identifies this data insight chart.'),
    ]
    displayName: Annotated[
        Optional[str], Field(None, description='Display Name the data insight chart.')
    ]
    fullyQualifiedName: Annotated[
        Optional[basic.FullyQualifiedEntityName],
        Field(None, description='FullyQualifiedName same as `name`.'),
    ]
    description: Annotated[
        Optional[basic.Markdown],
        Field(None, description='Description of the data insight chart.'),
    ]
    chartType: Annotated[
        Optional[ChartType],
        Field(None, description='Type of chart, used for UI to render the chart'),
    ]
    chartDetails: Union[lineChart.LineChart, summaryCard.SummaryCard]
    isSystemChart: Annotated[
        Optional[bool],
        Field(
            False,
            description='Flag to indicate if the chart is system generated or user created.',
        ),
    ]
    owner: Annotated[
        Optional[entityReference.EntityReference],
        Field(None, description='Owner of this chart'),
    ]
    version: Annotated[
        Optional[entityHistory.EntityVersion],
        Field(None, description='Metadata version of the entity.'),
    ]
    updatedAt: Annotated[
        Optional[basic.Timestamp],
        Field(
            None,
            description='Last update time corresponding to the new version of the entity in Unix epoch time milliseconds.',
        ),
    ]
    updatedBy: Annotated[
        Optional[str], Field(None, description='User who made the update.')
    ]
    href: Annotated[
        Optional[basic.Href],
        Field(None, description='Link to the resource corresponding to this entity.'),
    ]
    changeDescription: Annotated[
        Optional[entityHistory.ChangeDescription],
        Field(None, description='Change that lead to this version of the entity.'),
    ]
    deleted: Annotated[
        Optional[bool],
        Field(
            False, description='When `true` indicates the entity has been soft deleted.'
        ),
    ]
    dashboard: Annotated[
        Optional[entityReference.EntityReference],
        Field(None, description='Dashboard where this chart is displayed'),
    ]
