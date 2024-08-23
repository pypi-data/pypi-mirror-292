# generated by datamodel-codegen:
#   filename:  api/createBot.json
#   timestamp: 2024-08-22T13:36:48+00:00

from __future__ import annotations

from typing import Optional

from pydantic import ConfigDict, Field
from typing_extensions import Annotated

from metadata.ingestion.models.custom_pydantic import BaseModel

from ..type import basic


class CreateBot(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    name: Annotated[basic.EntityName, Field(description='Name of the bot.')]
    displayName: Annotated[
        Optional[str],
        Field(
            None,
            description="Name used for display purposes. Example 'FirstName LastName'.",
        ),
    ]
    botUser: Annotated[
        str,
        Field(
            description='Bot user name created for this bot on behalf of which the bot performs all the operations, such as updating description, responding on the conversation threads, etc.'
        ),
    ]
    description: Annotated[
        Optional[str], Field(None, description='Description of the bot.')
    ]
    provider: Optional[basic.ProviderType] = basic.ProviderType.user
    domain: Annotated[
        Optional[str],
        Field(
            None, description='Fully qualified name of the domain the Table belongs to.'
        ),
    ]
