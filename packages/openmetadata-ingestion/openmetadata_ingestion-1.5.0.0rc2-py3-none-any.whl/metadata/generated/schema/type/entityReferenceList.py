# generated by datamodel-codegen:
#   filename:  type/entityReferenceList.json
#   timestamp: 2024-08-22T13:36:48+00:00

from __future__ import annotations

from typing import List

from pydantic import Field, RootModel
from typing_extensions import Annotated

from . import entityReference


class EntityReferenceList(RootModel[List[entityReference.EntityReference]]):
    root: Annotated[
        List[entityReference.EntityReference],
        Field(
            description='This schema defines the EntityReferenceList type used for referencing an entity. EntityReference is used for capturing relationships from one entity to another. For example, a table has an attribute called database of type EntityReference that captures the relationship of a table `belongs to a` database.',
            title='Entity Reference List',
        ),
    ]
