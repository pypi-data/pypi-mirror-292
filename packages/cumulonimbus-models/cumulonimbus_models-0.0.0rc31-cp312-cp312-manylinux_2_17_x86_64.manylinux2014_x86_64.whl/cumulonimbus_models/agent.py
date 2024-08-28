from typing import ClassVar, Literal
from pydantic.main import BaseModel
from cumulonimbus_models.api import APIRequest


class AgentRegisterRequest(APIRequest):
    route_format: ClassVar[str] = '/agent/register'
    hostname: str


class AgentRegisterResponse(BaseModel):
    agent_id: str
    agent_key: str
    ip_address: str
    operations_queue_url: str


class UnregisterAgentRequest(APIRequest):
    route_format: ClassVar[str] = '/agent/{agent_id}'


UnregisterAgentStatus = Literal['NOT_FOUND', 'SUCCESS']



class UnregisterAgentResponse(BaseModel):
    status: UnregisterAgentStatus

