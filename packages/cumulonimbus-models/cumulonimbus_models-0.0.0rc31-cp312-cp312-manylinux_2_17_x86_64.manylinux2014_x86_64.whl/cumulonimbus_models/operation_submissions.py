from typing import ClassVar

from pydantic.main import BaseModel

from cumulonimbus_models.operations import OperationType, SubmitOperationRequest


class SubmitUpdateOperationRequest(SubmitOperationRequest):
    type: ClassVar[OperationType] = OperationType.UPDATE
    parameters: dict[str, str] = {}


class ShellCommandOperationParameters(BaseModel):
    command: str
    args: list[str] = []


class SubmitShellCommandOperationRequest(SubmitOperationRequest):
    type: ClassVar[OperationType] = OperationType.SHELL_COMMAND
    parameters: ShellCommandOperationParameters

