# generated by datamodel-codegen:
#   filename:  entity/automations/testServiceConnection.json
#   timestamp: 2024-08-22T13:36:48+00:00

from __future__ import annotations

from typing import Optional, Union

from pydantic import ConfigDict, Field
from typing_extensions import Annotated

from metadata.ingestion.models.custom_pydantic import BaseModel

from ...security.secrets import secretsManagerProvider
from ...type import basic
from ..services import (
    dashboardService,
    databaseService,
    messagingService,
    metadataService,
    mlmodelService,
    pipelineService,
    searchService,
    serviceType,
    storageService,
)


class TestServiceConnectionRequest(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    connection: Annotated[
        Optional[
            Union[
                databaseService.DatabaseConnection,
                dashboardService.DashboardConnection,
                messagingService.MessagingConnection,
                pipelineService.PipelineConnection,
                mlmodelService.MlModelConnection,
                metadataService.MetadataConnection,
                storageService.StorageConnection,
                searchService.SearchConnection,
            ]
        ],
        Field(None, description='Connection object.'),
    ]
    serviceType: Annotated[
        Optional[serviceType.ServiceType],
        Field(
            None,
            description='Type of service such as Database, Dashboard, Messaging, etc.',
        ),
    ]
    connectionType: Annotated[
        Optional[str],
        Field(
            None,
            description='Type of the connection to test such as Snowflake, MySQL, Looker, etc.',
        ),
    ]
    serviceName: Annotated[
        Optional[basic.EntityName],
        Field(None, description='Optional value that identifies this service name.'),
    ]
    secretsManagerProvider: Annotated[
        Optional[secretsManagerProvider.SecretsManagerProvider],
        Field(
            secretsManagerProvider.SecretsManagerProvider.db,
            description='Secrets Manager Provider to use for fetching secrets.',
        ),
    ]
