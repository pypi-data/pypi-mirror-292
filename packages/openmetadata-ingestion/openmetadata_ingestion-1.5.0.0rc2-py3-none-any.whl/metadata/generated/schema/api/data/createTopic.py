# generated by datamodel-codegen:
#   filename:  api/data/createTopic.json
#   timestamp: 2024-08-22T13:36:48+00:00

from __future__ import annotations

from typing import List, Optional

from pydantic import ConfigDict, Field
from typing_extensions import Annotated

from metadata.ingestion.models.custom_pydantic import BaseModel

from ...entity.data import topic
from ...type import basic, entityReferenceList, lifeCycle, schema, tagLabel


class CreateTopicRequest(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    name: Annotated[
        basic.EntityName,
        Field(description='Name that identifies this topic instance uniquely.'),
    ]
    displayName: Annotated[
        Optional[str],
        Field(None, description='Display Name that identifies this topic.'),
    ]
    description: Annotated[
        Optional[basic.Markdown],
        Field(
            None,
            description='Description of the topic instance. What it has and how to use it.',
        ),
    ]
    service: Annotated[
        basic.FullyQualifiedEntityName,
        Field(
            description='Fully qualified name of the messaging service where this topic is hosted in'
        ),
    ]
    messageSchema: Optional[schema.Topic] = None
    partitions: Annotated[
        int,
        Field(
            description='Number of partitions into which the topic is divided.', ge=1
        ),
    ]
    cleanupPolicies: Annotated[
        Optional[List[topic.CleanupPolicy]],
        Field(
            None,
            description='Topic clean up policy. For Kafka - `cleanup.policy` configuration.',
        ),
    ]
    replicationFactor: Annotated[
        Optional[int],
        Field(None, description='Replication Factor in integer (more than 1).'),
    ]
    retentionTime: Annotated[
        Optional[float],
        Field(
            None,
            description='Retention time in milliseconds. For Kafka - `retention.ms` configuration.',
        ),
    ]
    maximumMessageSize: Annotated[
        Optional[int],
        Field(
            None,
            description='Maximum message size in bytes. For Kafka - `max.message.bytes` configuration.',
        ),
    ]
    minimumInSyncReplicas: Annotated[
        Optional[int],
        Field(
            None,
            description='Minimum number replicas in sync to control durability. For Kafka - `min.insync.replicas` configuration.',
        ),
    ]
    retentionSize: Annotated[
        Optional[float],
        Field(
            '-1',
            description='Maximum size of a partition in bytes before old data is discarded. For Kafka - `retention.bytes` configuration.',
        ),
    ]
    topicConfig: Annotated[
        Optional[topic.TopicConfig],
        Field(None, description='Contains key/value pair of topic configuration.'),
    ]
    owners: Annotated[
        Optional[entityReferenceList.EntityReferenceList],
        Field(None, description='Owners of this topic'),
    ]
    tags: Annotated[
        Optional[List[tagLabel.TagLabel]],
        Field(None, description='Tags for this topic'),
    ]
    extension: Annotated[
        Optional[basic.EntityExtension],
        Field(
            None,
            description='Entity extension data with custom attributes added to the entity.',
        ),
    ]
    sourceUrl: Annotated[
        Optional[basic.SourceUrl], Field(None, description='Source URL of topic.')
    ]
    domain: Annotated[
        Optional[basic.FullyQualifiedEntityName],
        Field(
            None, description='Fully qualified name of the domain the Topic belongs to.'
        ),
    ]
    dataProducts: Annotated[
        Optional[List[basic.FullyQualifiedEntityName]],
        Field(
            None,
            description='List of fully qualified names of data products this entity is part of.',
        ),
    ]
    lifeCycle: Annotated[
        Optional[lifeCycle.LifeCycle],
        Field(None, description='Life Cycle of the entity'),
    ]
    sourceHash: Annotated[
        Optional[str],
        Field(
            None, description='Source hash of the entity', max_length=32, min_length=1
        ),
    ]
