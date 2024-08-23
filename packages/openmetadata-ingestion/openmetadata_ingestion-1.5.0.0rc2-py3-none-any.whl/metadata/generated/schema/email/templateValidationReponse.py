# generated by datamodel-codegen:
#   filename:  email/templateValidationReponse.json
#   timestamp: 2024-08-22T13:36:48+00:00

from __future__ import annotations

from typing import List, Optional

from pydantic import ConfigDict, Field
from typing_extensions import Annotated

from metadata.ingestion.models.custom_pydantic import BaseModel


class EmailTemplateValidationReponse(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    isValid: Annotated[
        Optional[bool],
        Field(None, description='Flag indicating if the template is valid.'),
    ]
    missingPlaceholder: Annotated[
        Optional[List[str]], Field(None, description='List of missing placeholders.')
    ]
    additionalPlaceholder: Annotated[
        Optional[List[str]], Field(None, description='List of additional placeholders.')
    ]
    message: Annotated[Optional[str], Field(None, description='Validation message.')]
