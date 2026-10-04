from datetime import datetime, time
from uuid import UUID

from pydantic import BaseModel, Field

from app.schemas.user import ORMModel


class SupervisorCreate(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    active: bool = True


class SupervisorUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=120)
    active: bool | None = None


class SupervisorRead(ORMModel):
    id: UUID
    name: str
    active: bool
    created_at: datetime
    updated_at: datetime


class MachineCreate(BaseModel):
    code: str = Field(min_length=1, max_length=40)
    name: str | None = Field(default=None, max_length=120)
    active: bool = True


class MachineUpdate(BaseModel):
    code: str | None = Field(default=None, min_length=1, max_length=40)
    name: str | None = None
    active: bool | None = None


class MachineRead(ORMModel):
    id: UUID
    code: str
    name: str | None
    active: bool
    created_at: datetime
    updated_at: datetime


class ShiftCreate(BaseModel):
    code: str = Field(min_length=1, max_length=8)
    name: str = Field(min_length=1, max_length=80)
    start_time: time
    end_time: time
    crosses_midnight: bool = False
    sort_order: int = 0
    active: bool = True


class ShiftUpdate(BaseModel):
    code: str | None = None
    name: str | None = None
    start_time: time | None = None
    end_time: time | None = None
    crosses_midnight: bool | None = None
    sort_order: int | None = None
    active: bool | None = None


class ShiftRead(ORMModel):
    id: UUID
    code: str
    name: str
    start_time: time
    end_time: time
    crosses_midnight: bool
    sort_order: int
    active: bool


class ReasonCreate(BaseModel):
    name: str = Field(min_length=1, max_length=160)
    requires_details: bool = False
    details_label: str | None = None
    measurement_type: str = "duration_minutes"
    sort_order: int = 0
    notes: str | None = None
    active: bool = True


class ReasonUpdate(BaseModel):
    name: str | None = None
    requires_details: bool | None = None
    details_label: str | None = None
    measurement_type: str | None = None
    sort_order: int | None = None
    notes: str | None = None
    active: bool | None = None


class ReasonRead(ORMModel):
    id: UUID
    name: str
    requires_details: bool
    details_label: str | None
    measurement_type: str
    sort_order: int
    notes: str | None
    active: bool
