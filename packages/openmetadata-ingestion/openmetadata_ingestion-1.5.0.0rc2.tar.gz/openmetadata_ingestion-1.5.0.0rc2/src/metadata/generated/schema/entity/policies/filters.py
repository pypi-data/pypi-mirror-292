# generated by datamodel-codegen:
#   filename:  entity/policies/filters.json
#   timestamp: 2024-08-22T13:36:48+00:00

from __future__ import annotations

from typing import Any, List

from pydantic import Field, RootModel
from typing_extensions import Annotated

from ...type import basic


class Filters(RootModel[Any]):
    root: Annotated[Any, Field(title='Filters')]


class Prefix(RootModel[str]):
    root: Annotated[str, Field(description='Prefix path of the entity.')]


class Regex(RootModel[str]):
    root: Annotated[str, Field(description='Regex that matches the entity.')]


class Tags(RootModel[List[basic.EntityName]]):
    root: Annotated[
        List[basic.EntityName],
        Field(description='Set of tags to match on (OR among all tags).'),
    ]
