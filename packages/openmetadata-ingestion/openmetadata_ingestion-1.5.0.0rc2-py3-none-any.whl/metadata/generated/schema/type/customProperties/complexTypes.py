# generated by datamodel-codegen:
#   filename:  type/customProperties/complexTypes.json
#   timestamp: 2024-08-22T13:36:48+00:00

from __future__ import annotations

from typing import Any, List, Optional, Union
from uuid import UUID

from pydantic import AnyUrl, Field, RootModel
from typing_extensions import Annotated

from metadata.ingestion.models.custom_pydantic import BaseModel


class Basic(RootModel[Any]):
    root: Annotated[
        Any,
        Field(
            description='This schema defines custom properties complex types.',
            title='Basic',
        ),
    ]


class EntityReference(BaseModel):
    id: Annotated[
        Optional[UUID],
        Field(
            None, description='Unique identifier that identifies an entity instance.'
        ),
    ]
    type: Annotated[
        Optional[str],
        Field(
            None,
            description='Entity type/class name - Examples: `database`, `table`, `metrics`, `databaseService`, `dashboardService`...',
        ),
    ]
    name: Annotated[
        Optional[str], Field(None, description='Name of the entity instance.')
    ]
    fullyQualifiedName: Annotated[
        Optional[str],
        Field(
            None,
            description="Fully qualified name of the entity instance. For entities such as tables, databases fullyQualifiedName is returned in this field. For entities that don't have name hierarchy such as `user` and `team` this will be same as the `name` field.",
        ),
    ]
    description: Annotated[
        Optional[str], Field(None, description='Optional description of entity.')
    ]
    displayName: Annotated[
        Optional[str],
        Field(None, description='Display Name that identifies this entity.'),
    ]
    deleted: Annotated[
        Optional[bool],
        Field(
            None, description='If true the entity referred to has been soft-deleted.'
        ),
    ]
    inherited: Annotated[
        Optional[bool],
        Field(
            None,
            description='If true the relationship indicated by this entity reference is inherited from the parent entity.',
        ),
    ]
    href: Annotated[
        Optional[AnyUrl], Field(None, description='Link to the entity resource.')
    ]


class Items(BaseModel):
    id: Annotated[
        Optional[UUID],
        Field(
            None, description='Unique identifier that identifies an entity instance.'
        ),
    ]
    type: Annotated[
        Optional[str],
        Field(
            None,
            description='Entity type/class name - Examples: `database`, `table`, `metrics`, `databaseService`, `dashboardService`...',
        ),
    ]
    name: Annotated[
        Optional[str], Field(None, description='Name of the entity instance.')
    ]
    fullyQualifiedName: Annotated[
        Optional[str],
        Field(
            None,
            description="Fully qualified name of the entity instance. For entities such as tables, databases fullyQualifiedName is returned in this field. For entities that don't have name hierarchy such as `user` and `team` this will be same as the `name` field.",
        ),
    ]
    description: Annotated[
        Optional[str], Field(None, description='Optional description of entity.')
    ]
    displayName: Annotated[
        Optional[str],
        Field(None, description='Display Name that identifies this entity.'),
    ]
    deleted: Annotated[
        Optional[bool],
        Field(
            None, description='If true the entity referred to has been soft-deleted.'
        ),
    ]
    inherited: Annotated[
        Optional[bool],
        Field(
            None,
            description='If true the relationship indicated by this entity reference is inherited from the parent entity.',
        ),
    ]
    href: Annotated[
        Optional[AnyUrl], Field(None, description='Link to the entity resource.')
    ]


class EntityReferenceList(BaseModel):
    items: Optional[Items] = None


class EntityReferenceList1(RootModel[Union[List, EntityReferenceList]]):
    root: Annotated[
        Union[List, EntityReferenceList],
        Field(description='Entity Reference List for Custom Property.'),
    ]
