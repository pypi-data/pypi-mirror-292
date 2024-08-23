# generated by datamodel-codegen:
#   filename:  events/api/createEventSubscription.json
#   timestamp: 2024-08-22T13:36:48+00:00

from __future__ import annotations

from typing import List, Optional

from pydantic import ConfigDict, Field
from typing_extensions import Annotated

from metadata.ingestion.models.custom_pydantic import BaseModel

from ...type import basic, entityReferenceList
from .. import eventSubscription


class CreateEventSubscription(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    name: Annotated[
        basic.EntityName, Field(description='Name that uniquely identifies this Alert.')
    ]
    displayName: Annotated[
        Optional[str], Field(None, description='Display name for this Alert.')
    ]
    description: Annotated[
        Optional[basic.Markdown],
        Field(
            None,
            description='A short description of the Alert, comprehensible to regular users.',
        ),
    ]
    owners: Annotated[
        Optional[entityReferenceList.EntityReferenceList],
        Field(None, description='Owners of this Alert.'),
    ]
    enabled: Annotated[Optional[bool], Field(True, description='Is the alert enabled.')]
    batchSize: Annotated[
        Optional[int],
        Field(10, description='Maximum number of events sent in a batch (Default 10).'),
    ]
    alertType: Annotated[
        eventSubscription.AlertType, Field(description='Type of Alert')
    ]
    trigger: Optional[eventSubscription.Trigger] = None
    resources: Annotated[
        Optional[List[str]],
        Field(
            None,
            description='Defines a list of resources that triggers the Event Subscription, Eg All, User, Teams etc.',
        ),
    ]
    destinations: Annotated[
        Optional[List[eventSubscription.Destination]],
        Field(None, description='Subscription Config.'),
    ]
    provider: Optional[basic.ProviderType] = basic.ProviderType.user
    retries: Annotated[
        Optional[int],
        Field(
            3, description='Number of times to retry callback on failure. (Default 3).'
        ),
    ]
    pollInterval: Annotated[
        Optional[int], Field(10, description='Poll Interval in seconds.')
    ]
    input: Annotated[
        Optional[eventSubscription.AlertFilteringInput],
        Field(None, description='Input for the Filters.'),
    ]
    domain: Annotated[
        Optional[str],
        Field(
            None, description='Fully qualified name of the domain the Table belongs to.'
        ),
    ]
