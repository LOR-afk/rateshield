from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


class PolicyUpdate(BaseModel):
    max_requests: int = Field(ge=1, le=1000)
    window_seconds: int = Field(ge=1, le=3600)
    failed_login_threshold: int = Field(ge=1, le=100)


class PolicyOut(PolicyUpdate):
    model_config = ConfigDict(from_attributes=True)
    id: int


class EventOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    client_ip: str
    kind: str
    endpoint: str
    status_code: int
    detail: str
    created_at: datetime


class DemoLogin(BaseModel):
    success: bool = False
