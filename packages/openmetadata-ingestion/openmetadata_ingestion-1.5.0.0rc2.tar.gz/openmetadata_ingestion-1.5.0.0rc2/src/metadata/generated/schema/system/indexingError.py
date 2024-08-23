# generated by datamodel-codegen:
#   filename:  system/indexingError.json
#   timestamp: 2024-08-22T13:36:48+00:00

from __future__ import annotations

from enum import Enum
from typing import List, Optional

from pydantic import ConfigDict

from metadata.ingestion.models.custom_pydantic import BaseModel

from . import entityError


class ErrorSource(Enum):
    Job = 'Job'
    Reader = 'Reader'
    Processor = 'Processor'
    Sink = 'Sink'


class IndexingAppError(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    errorSource: Optional[ErrorSource] = None
    lastFailedCursor: Optional[str] = None
    message: Optional[str] = None
    failedEntities: Optional[List[entityError.EntityError]] = None
    reason: Optional[str] = None
    stackTrace: Optional[str] = None
    submittedCount: Optional[int] = None
    successCount: Optional[int] = None
    failedCount: Optional[int] = None
