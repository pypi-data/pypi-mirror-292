# generated by datamodel-codegen:
#   filename:  events/eventSubscription.json
#   timestamp: 2024-08-22T13:36:48+00:00

from __future__ import annotations

from enum import Enum
from typing import List, Optional, Union

from pydantic import ConfigDict, Field
from typing_extensions import Annotated

from metadata.ingestion.models.custom_pydantic import BaseModel

from ..entity.events import webhook
from ..type import basic, entityHistory, entityReference, entityReferenceList
from . import emailAlertConfig, eventFilterRule


class Argument(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    name: Annotated[Optional[str], Field(None, description='Name of the Argument')]
    input: Annotated[
        Optional[List[str]], Field(None, description='Value of the Argument')
    ]


class ArgumentsInput(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    name: Annotated[Optional[str], Field(None, description='Name of the filter')]
    effect: Optional[eventFilterRule.Effect] = eventFilterRule.Effect.include
    prefixCondition: Annotated[
        Optional[eventFilterRule.PrefixCondition],
        Field(
            eventFilterRule.PrefixCondition.AND,
            description='Prefix Condition for the filter.',
        ),
    ]
    arguments: Annotated[
        Optional[List[Argument]], Field(None, description='Arguments List')
    ]


class AlertFilteringInput(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    filters: Annotated[
        Optional[List[ArgumentsInput]],
        Field(None, description='List of filters for the event subscription.'),
    ]
    actions: Annotated[
        Optional[List[ArgumentsInput]],
        Field(None, description='List of filters for the event subscription.'),
    ]


class TriggerType(Enum):
    RealTime = 'RealTime'
    Scheduled = 'Scheduled'


class AlertType(Enum):
    Notification = 'Notification'
    Observability = 'Observability'
    ActivityFeed = 'ActivityFeed'


class SubscriptionCategory(Enum):
    Users = 'Users'
    Teams = 'Teams'
    Admins = 'Admins'
    Assignees = 'Assignees'
    Owners = 'Owners'
    Mentions = 'Mentions'
    Followers = 'Followers'
    External = 'External'


class SubscriptionType(Enum):
    Webhook = 'Webhook'
    Slack = 'Slack'
    MsTeams = 'MsTeams'
    GChat = 'GChat'
    Email = 'Email'
    ActivityFeed = 'ActivityFeed'


class Status(Enum):
    disabled = 'disabled'
    failed = 'failed'
    retryLimitReached = 'retryLimitReached'
    awaitingRetry = 'awaitingRetry'
    active = 'active'


class SubscriptionStatus(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    status: Optional[Status] = None
    lastSuccessfulAt: Annotated[
        Optional[basic.Timestamp],
        Field(
            None,
            description='Last non-successful callback time in UNIX UTC epoch time in milliseconds.',
        ),
    ]
    lastFailedAt: Annotated[
        Optional[basic.Timestamp],
        Field(
            None,
            description='Last non-successful callback time in UNIX UTC epoch time in milliseconds.',
        ),
    ]
    lastFailedStatusCode: Annotated[
        Optional[int],
        Field(
            None,
            description='Last non-successful activity response code received during callback.',
        ),
    ]
    lastFailedReason: Annotated[
        Optional[str],
        Field(
            None,
            description='Last non-successful activity response reason received during callback.',
        ),
    ]
    nextAttempt: Annotated[
        Optional[basic.Timestamp],
        Field(
            None,
            description='Next retry will be done at this time in Unix epoch time milliseconds. Only valid is `status` is `awaitingRetry`.',
        ),
    ]
    timestamp: Optional[basic.Timestamp] = None


class ScheduleInfo(Enum):
    Daily = 'Daily'
    Weekly = 'Weekly'
    Monthly = 'Monthly'
    Custom = 'Custom'


class Trigger(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    triggerType: TriggerType
    scheduleInfo: Annotated[
        Optional[ScheduleInfo], Field(ScheduleInfo.Weekly, description='Schedule Info')
    ]
    cronExpression: Annotated[
        Optional[str],
        Field(None, description='Cron Expression in case of Custom scheduled Trigger'),
    ]


class Destination(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    id: Annotated[
        Optional[basic.Uuid],
        Field(
            None,
            description='Unique identifier that identifies this Event Subscription.',
        ),
    ]
    category: SubscriptionCategory
    type: SubscriptionType
    statusDetails: Optional[SubscriptionStatus] = None
    timeout: Annotated[
        Optional[int],
        Field(10, description='Connection timeout in seconds. (Default 10s).'),
    ]
    readTimeout: Annotated[
        Optional[int], Field(12, description='Read timeout in seconds. (Default 12s).')
    ]
    enabled: Annotated[
        Optional[bool], Field(True, description='Is the subscription enabled.')
    ]
    config: Optional[Union[webhook.Webhook, emailAlertConfig.EmailAlertConfig]] = None


class FilteringRules(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    resources: Annotated[
        List[str],
        Field(
            description='Defines a list of resources that triggers the Event Subscription, Eg All, User, Teams etc.'
        ),
    ]
    rules: Annotated[
        Optional[List[eventFilterRule.EventFilterRule]],
        Field(None, description='A set of filter rules associated with the Alert.'),
    ]
    actions: Annotated[
        Optional[List[eventFilterRule.EventFilterRule]],
        Field(None, description='A set of filter rules associated with the Alert.'),
    ]


class EventSubscription(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    id: Annotated[
        basic.Uuid,
        Field(description='Unique identifier that identifies this Event Subscription.'),
    ]
    name: Annotated[
        basic.EntityName,
        Field(description='Name that uniquely identifies this Event Subscription.'),
    ]
    fullyQualifiedName: Annotated[
        Optional[basic.FullyQualifiedEntityName],
        Field(
            None,
            description='FullyQualifiedName that uniquely identifies a Event Subscription.',
        ),
    ]
    displayName: Annotated[
        Optional[str],
        Field(None, description='Display name for this Event Subscription.'),
    ]
    description: Annotated[
        Optional[basic.Markdown],
        Field(
            None,
            description='A short description of the Event Subscription, comprehensible to regular users.',
        ),
    ]
    owners: Annotated[
        Optional[entityReferenceList.EntityReferenceList],
        Field(None, description='Owners of this Event Subscription.'),
    ]
    href: Annotated[
        Optional[basic.Href],
        Field(None, description='Link to the resource corresponding to this entity.'),
    ]
    version: Annotated[
        Optional[entityHistory.EntityVersion],
        Field(None, description='Metadata version of the Event Subscription.'),
    ]
    updatedAt: Annotated[
        Optional[basic.Timestamp],
        Field(
            None,
            description='Last update time corresponding to the new version of the Event Subscription in Unix epoch time milliseconds.',
        ),
    ]
    updatedBy: Annotated[
        Optional[str], Field(None, description='User who made the update.')
    ]
    changeDescription: Annotated[
        Optional[entityHistory.ChangeDescription],
        Field(
            None,
            description='Change that led to this version of the Event Subscription.',
        ),
    ]
    alertType: Annotated[AlertType, Field(description='Type of Alert')]
    trigger: Annotated[
        Optional[Trigger], Field(None, description='Trigger information for Alert.')
    ]
    filteringRules: Annotated[
        Optional[FilteringRules],
        Field(
            None,
            description='Set of rules that the Event Subscription Contains to allow conditional control for alerting.',
        ),
    ]
    destinations: Annotated[List[Destination], Field(description='Destination Config.')]
    enabled: Annotated[
        Optional[bool], Field(True, description='Is the event Subscription enabled.')
    ]
    batchSize: Annotated[
        Optional[int],
        Field(
            100, description='Maximum number of events sent in a batch (Default 100).'
        ),
    ]
    provider: Optional[basic.ProviderType] = basic.ProviderType.user
    retries: Annotated[
        Optional[int],
        Field(
            3, description='Number of times to retry callback on failure. (Default 3).'
        ),
    ]
    pollInterval: Annotated[
        Optional[int], Field(60, description='Poll Interval in seconds.')
    ]
    input: Annotated[
        Optional[AlertFilteringInput], Field(None, description='Input for the Filters.')
    ]
    domain: Annotated[
        Optional[entityReference.EntityReference],
        Field(
            None,
            description='Domain the asset belongs to. When not set, the asset inherits the domain from the parent it belongs to.',
        ),
    ]
