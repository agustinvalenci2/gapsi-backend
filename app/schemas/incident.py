from datetime import datetime

from app.models.incident import IncidenceStatus, Priority
from pydantic import BaseModel, ConfigDict, Field


class IncidentCreate(BaseModel):
    title: str = Field(min_length=1, max_length=100)
    description: str | None = Field(default=None, max_length=10000)
    priority: Priority = Priority.LOW
    status: IncidenceStatus = IncidenceStatus.PENDING

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


class IncidentRead(IncidentCreate):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class IncidentStatusCounts(BaseModel):
    pending: int = Field(default=0, ge=0)
    done: int = Field(default=0, ge=0)
    rejected: int = Field(default=0, ge=0)
    in_progress: int = Field(0, ge=0)


class IncidentSummary(BaseModel):
    total: int = Field(ge=0)
    by_status: IncidentStatusCounts
