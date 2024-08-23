# generated by datamodel-codegen:
#   filename:  tests/basic.json
#   timestamp: 2024-08-22T13:36:48+00:00

from __future__ import annotations

from enum import Enum
from typing import Any, List, Optional

from pydantic import Field, RootModel
from typing_extensions import Annotated

from metadata.ingestion.models.custom_pydantic import BaseModel

from ..type import basic


class Basic(RootModel[Any]):
    root: Annotated[
        Any,
        Field(
            description='This schema defines basic types that are used by other test schemas.',
            title='Basic',
        ),
    ]


class TestResultValue(BaseModel):
    name: Annotated[Optional[str], Field(None, description='name of the value')]
    value: Annotated[Optional[str], Field(None, description='test result value')]
    predictedValue: Annotated[Optional[str], Field(None, description='predicted value')]


class TestCaseStatus(Enum):
    Success = 'Success'
    Failed = 'Failed'
    Aborted = 'Aborted'
    Queued = 'Queued'


class TestSuiteExecutionFrequency(Enum):
    Hourly = 'Hourly'
    Daily = 'Daily'
    Weekly = 'Weekly'


class ColumnTestSummaryDefinition(BaseModel):
    success: Annotated[
        Optional[int], Field(None, description='Number of test cases that passed.')
    ]
    failed: Annotated[
        Optional[int], Field(None, description='Number of test cases that failed.')
    ]
    aborted: Annotated[
        Optional[int], Field(None, description='Number of test cases that aborted.')
    ]
    queued: Annotated[
        Optional[int],
        Field(None, description='Number of test cases that are queued for execution.'),
    ]
    total: Annotated[
        Optional[int], Field(None, description='Total number of test cases.')
    ]
    entityLink: Optional[basic.EntityLink] = None


class TestSummary(BaseModel):
    success: Annotated[
        Optional[int], Field(None, description='Number of test cases that passed.')
    ]
    failed: Annotated[
        Optional[int], Field(None, description='Number of test cases that failed.')
    ]
    aborted: Annotated[
        Optional[int], Field(None, description='Number of test cases that aborted.')
    ]
    queued: Annotated[
        Optional[int],
        Field(None, description='Number of test cases that are queued for execution.'),
    ]
    total: Annotated[
        Optional[int], Field(None, description='Total number of test cases.')
    ]
    columnTestSummary: Optional[List[ColumnTestSummaryDefinition]] = None


class TestCaseResult(BaseModel):
    timestamp: Annotated[
        Optional[basic.Timestamp],
        Field(None, description='Data one which test case result is taken.'),
    ]
    testCaseStatus: Annotated[
        Optional[TestCaseStatus], Field(None, description='Status of Test Case run.')
    ]
    result: Annotated[
        Optional[str], Field(None, description='Details of test case results.')
    ]
    sampleData: Annotated[
        Optional[str],
        Field(
            None,
            description="sample data to capture rows/columns that didn't match the expressed testcase.",
        ),
    ]
    testResultValue: Optional[List[TestResultValue]] = None
    passedRows: Annotated[
        Optional[int], Field(None, description='Number of rows that passed.')
    ]
    failedRows: Annotated[
        Optional[int], Field(None, description='Number of rows that failed.')
    ]
    passedRowsPercentage: Annotated[
        Optional[float], Field(None, description='Percentage of rows that passed.')
    ]
    failedRowsPercentage: Annotated[
        Optional[float], Field(None, description='Percentage of rows that failed.')
    ]
    incidentId: Annotated[
        Optional[basic.Uuid],
        Field(
            None,
            description='Incident State ID associated with this result. This association happens when the result is created, and will stay there even when the incident is resolved.',
        ),
    ]
    maxBound: Annotated[
        Optional[float],
        Field(
            None,
            description='Upper bound limit for the test case result as defined in the test definition.',
        ),
    ]
    minBound: Annotated[
        Optional[float],
        Field(
            None,
            description='Lower bound limit for the test case result as defined in the test definition.',
        ),
    ]
