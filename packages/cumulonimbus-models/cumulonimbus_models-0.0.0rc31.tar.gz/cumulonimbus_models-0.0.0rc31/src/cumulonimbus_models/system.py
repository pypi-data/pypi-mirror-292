from typing import ClassVar, Literal

from pydantic.main import BaseModel

from cumulonimbus_models.api import APIRequest



SoftwareInstallationMethod = Literal[
    'PIP',
    'MANUAL',
    'APT',
    'GIT'
]


class Software(BaseModel):
    name: str
    version: str
    installation_method: SoftwareInstallationMethod
    installation_data: dict[str, str]
    config_data: dict[str, str]


class SystemInfo(BaseModel):
    os: str
    hostname: str
    software: list[Software]


# noinspection PyMethodOverriding,PyUnusedClass
class SystemUpdateRequest(APIRequest):
    route_format: ClassVar[str] = '/agent/{agent_id}/system_update'
    system_info: SystemInfo

