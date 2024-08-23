# generated by datamodel-codegen:
#   filename:  dataInsight/type/aggregatedUnusedAssetsCount.json
#   timestamp: 2024-08-22T13:36:48+00:00

from __future__ import annotations

from typing import Optional

from pydantic import ConfigDict, Field
from typing_extensions import Annotated

from metadata.ingestion.models.custom_pydantic import BaseModel

from ...analytics.reportDataType import aggregatedCostAnalysisReportData
from ...type import basic


class AggregatedUnusedAssetsCount(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    timestamp: Annotated[
        Optional[basic.Timestamp], Field(None, description='timestamp')
    ]
    frequentlyUsedDataAssets: Annotated[
        Optional[aggregatedCostAnalysisReportData.DataAssetValues],
        Field(None, description='Frequently used Data Assets'),
    ]
    unusedDataAssets: Annotated[
        Optional[aggregatedCostAnalysisReportData.DataAssetValues],
        Field(None, description='Unused Data Assets'),
    ]
