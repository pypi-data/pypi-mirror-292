# generated by datamodel-codegen:
#   filename:  api/data/createGlossaryTerm.json
#   timestamp: 2024-08-22T13:36:48+00:00

from __future__ import annotations

from typing import List, Optional

from pydantic import ConfigDict, Field
from typing_extensions import Annotated

from metadata.ingestion.models.custom_pydantic import BaseModel

from ...entity.data import glossaryTerm
from ...type import basic, entityReferenceList, tagLabel


class CreateGlossaryTermRequest(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    glossary: Annotated[
        basic.FullyQualifiedEntityName,
        Field(
            description='FullyQualifiedName of the glossary that this term is part of.'
        ),
    ]
    parent: Annotated[
        Optional[basic.FullyQualifiedEntityName],
        Field(None, description='Fully qualified name of  the parent glossary term.'),
    ]
    name: Annotated[
        basic.EntityName, Field(description='Preferred name for the glossary term.')
    ]
    displayName: Annotated[
        Optional[str],
        Field(None, description='Display Name that identifies this glossary term.'),
    ]
    description: Annotated[
        basic.Markdown, Field(description='Description of the glossary term.')
    ]
    style: Optional[basic.Style] = None
    synonyms: Annotated[
        Optional[List[basic.EntityName]],
        Field(
            None,
            description='Alternate names that are synonyms or near-synonyms for the glossary term.',
        ),
    ]
    relatedTerms: Annotated[
        Optional[List[basic.FullyQualifiedEntityName]],
        Field(
            None,
            description='Other array of glossary term fully qualified names that are related to this glossary term.',
        ),
    ]
    references: Annotated[
        Optional[List[glossaryTerm.TermReference]],
        Field(None, description='Link to a reference from an external glossary.'),
    ]
    reviewers: Annotated[
        Optional[entityReferenceList.EntityReferenceList],
        Field(
            None,
            description='User or Team references of the reviewers for this glossary.',
        ),
    ]
    owners: Annotated[
        Optional[entityReferenceList.EntityReferenceList],
        Field(None, description='Owners of this glossary term.'),
    ]
    tags: Annotated[
        Optional[List[tagLabel.TagLabel]],
        Field(None, description='Tags for this glossary term.'),
    ]
    provider: Optional[basic.ProviderType] = basic.ProviderType.user
    mutuallyExclusive: Annotated[
        Optional[bool],
        Field(
            'false',
            description='Glossary terms that are children of this term are mutually exclusive. When mutually exclusive is `true` only one term can be used to label an entity from this group. When mutually exclusive is `false`, multiple terms from this group can be used to label an entity.',
        ),
    ]
    extension: Annotated[
        Optional[basic.EntityExtension],
        Field(
            None,
            description='Entity extension data with custom attributes added to the entity.',
        ),
    ]
