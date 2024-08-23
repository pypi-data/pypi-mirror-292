# generated by datamodel-codegen:
#   filename:  email/smtpSettings.json
#   timestamp: 2024-08-22T13:36:48+00:00

from __future__ import annotations

from enum import Enum
from typing import Optional

from pydantic import ConfigDict, Field
from typing_extensions import Annotated

from metadata.ingestion.models.custom_pydantic import BaseModel


class TransportationStrategy(Enum):
    SMTP = 'SMTP'
    SMTPS = 'SMTPS'
    SMTP_TLS = 'SMTP_TLS'


class Templates(Enum):
    openmetadata = 'openmetadata'
    collate = 'collate'


class SmtpSettings(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    emailingEntity: Annotated[
        Optional[str], Field('OpenMetadata', description='Emailing Entity')
    ]
    supportUrl: Annotated[
        Optional[str],
        Field('https://slack.open-metadata.org', description='Support Url'),
    ]
    enableSmtpServer: Annotated[
        Optional[bool],
        Field(
            False,
            description='If this is enable password will details will be shared on mail',
        ),
    ]
    openMetadataUrl: Annotated[str, Field(description='Openmetadata Server Endpoint')]
    senderMail: Annotated[str, Field(description='Mail of the sender')]
    serverEndpoint: Annotated[str, Field(description='Smtp Server Endpoint')]
    serverPort: Annotated[int, Field(description='Smtp Server Port')]
    username: Annotated[Optional[str], Field(None, description='Smtp Server Username')]
    password: Annotated[Optional[str], Field(None, description='Smtp Server Password')]
    transportationStrategy: Optional[
        TransportationStrategy
    ] = TransportationStrategy.SMTP
    templatePath: Optional[str] = None
    templates: Optional[Templates] = Templates.openmetadata
