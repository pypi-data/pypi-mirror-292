from datetime import datetime
from enum import Enum
from typing import ClassVar, NamedTuple, Optional

from pydantic.main import BaseModel

from cumulonimbus_models.api import APIRequest


class OperationBase(BaseModel):
    agent_id: str
    operation_id: str



class OperationResultStatus(Enum):
    PENDING = 'PENDING'
    SUCCESS = 'SUCCESS'
    FAILURE = 'FAILURE'



class OperationType(Enum):
    UPDATE = 'UPDATE'
    SHELL_COMMAND = 'SHELL_COMMAND'



class Operation(BaseModel):
    id: str
    type: OperationType
    parameters: NamedTuple


class ShellCommandOperationParameters(NamedTuple):
    command: str


class ShellCommandOperation(Operation):
    parameters: ShellCommandOperationParameters



class SubmitOperationRequest(APIRequest):
    route_format: ClassVar[str] = '/agent/{agent_id}/operation/submit'
    type: ClassVar[OperationType]


class SubmitOperationResponse(BaseModel):
    operation_id: str
    submitted: datetime


class OperationResult(BaseModel):
    operation_output: str
    display_output: Optional[str] = None
    operation_status: OperationResultStatus
    result_data: Optional[dict[str, str]] = None

    '''
    @model_validator(mode='after')
    def validate_outputs(self) -> 'OperationResult':
        if self.display_output is None:
            self.display_output = self.operation_output
        return self
    '''


class UpdateOperationResultRequest(APIRequest):
    route_format: ClassVar[str] = '/agent/{agent_id}/operation/{operation_id}/result'
    started: datetime
    completed: datetime
    operation_result: OperationResult
