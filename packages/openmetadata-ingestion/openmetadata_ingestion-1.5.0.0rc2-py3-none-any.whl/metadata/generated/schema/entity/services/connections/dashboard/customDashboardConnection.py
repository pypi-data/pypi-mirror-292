# generated by datamodel-codegen:
#   filename:  entity/services/connections/dashboard/customDashboardConnection.json
#   timestamp: 2024-08-22T13:36:48+00:00

from __future__ import annotations

from enum import Enum
from typing import Optional

from pydantic import ConfigDict, Field
from typing_extensions import Annotated

from metadata.ingestion.models.custom_pydantic import BaseModel

from .. import connectionBasicType


class CustomDashboardType(Enum):
    CustomDashboard = 'CustomDashboard'


class CustomDashboardConnection(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    type: Annotated[
        CustomDashboardType,
        Field(description='Custom dashboard service type', title='Service Type'),
    ]
    sourcePythonClass: Annotated[
        Optional[str],
        Field(
            None,
            description='Source Python Class Name to instantiated by the ingestion workflow',
            title='Source Python Class Name',
        ),
    ]
    connectionOptions: Annotated[
        Optional[connectionBasicType.ConnectionOptions],
        Field(None, title='Connection Options'),
    ]
