# generated by datamodel-codegen:
#   filename:  api/domains/createDomain.json
#   timestamp: 2024-08-22T13:36:48+00:00

from __future__ import annotations

from typing import List, Optional

from pydantic import ConfigDict, Field
from typing_extensions import Annotated

from metadata.ingestion.models.custom_pydantic import BaseModel

from ...entity.domains import domain
from ...type import basic, entityReferenceList


class CreateDomainRequest(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    domainType: Annotated[domain.DomainType, Field(description='Domain type')]
    name: Annotated[basic.EntityName, Field(description='A unique name of the Domain')]
    fullyQualifiedName: Annotated[
        Optional[basic.FullyQualifiedEntityName],
        Field(None, description='FullyQualifiedName same as `name`.'),
    ]
    displayName: Annotated[
        Optional[str],
        Field(
            None,
            description="Name used for display purposes. Example 'Marketing', 'Payments', etc.",
        ),
    ]
    description: Annotated[
        basic.Markdown, Field(description='Description of the Domain.')
    ]
    style: Optional[basic.Style] = None
    parent: Annotated[
        Optional[str], Field(None, description='Fully qualified name of parent domain.')
    ]
    owners: Annotated[
        Optional[entityReferenceList.EntityReferenceList],
        Field(None, description='Owners of this Domain.'),
    ]
    experts: Annotated[
        Optional[List[str]],
        Field(
            None,
            description='List of user/login names of users who are experts in this Domain.',
        ),
    ]
