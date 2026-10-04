from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field, field_validator

from app.schemas.master import MachineRead, ReasonRead, ShiftRead, SupervisorRead
from app.schemas.user import ORMModel


class StoppageCreate(BaseModel):
    production_date: date
    shift_id: UUID
    supervisor_id: UUID
    machine_id: UUID
    stoppage_reason_id: UUID
    duration_minutes: Decimal = Field(gt=0)
    details: str | None = Field(default=None, max_length=2000)
    remarks: str | None = Field(default=None, max_length=4000)

    @field_validator("duration_minutes")
    @classmethod
    def integer_minutes_for_now(cls, value: Decimal) -> Decimal:
        if value != value.to_integral_value():
            raise ValueError("Please enter the stoppage duration in whole minutes.")
        if value <= 0:
            raise ValueError("Duration must be greater than 0 minutes.")
        return value


class StoppageUpdate(BaseModel):
    production_date: date | None = None
    shift_id: UUID | None = None
    supervisor_id: UUID | None = None
    machine_id: UUID | None = None
    stoppage_reason_id: UUID | None = None
    duration_minutes: Decimal | None = Field(default=None, gt=0)
    details: str | None = Field(default=None, max_length=2000)
    remarks: str | None = Field(default=None, max_length=4000)

    @field_validator("duration_minutes")
    @classmethod
    def integer_minutes_for_now(cls, value: Decimal | None) -> Decimal | None:
        if value is None:
            return value
        if value != value.to_integral_value():
            raise ValueError("Please enter the stoppage duration in whole minutes.")
        if value <= 0:
            raise ValueError("Duration must be greater than 0 minutes.")
        return value


class StoppageRead(ORMModel):
    id: UUID
    production_date: date
    shift_id: UUID
    supervisor_id: UUID
    machine_id: UUID
    stoppage_reason_id: UUID
    duration_minutes: Decimal
    details: str | None
    remarks: str | None
    created_at: datetime
    updated_at: datetime
    created_by: UUID | None
    updated_by: UUID | None
    shift: ShiftRead
    supervisor: SupervisorRead
    machine: MachineRead
    reason: ReasonRead


class StoppageFilters(BaseModel):
    date_from: date | None = None
    date_to: date | None = None
    shift_id: UUID | None = None
    supervisor_id: UUID | None = None
    machine_id: UUID | None = None
    reason_id: UUID | None = None
    search: str | None = None
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=25, ge=1, le=100)
    sort_by: str = "created_at"
    sort_order: str = "desc"


class PaginationMeta(BaseModel):
    page: int
    page_size: int
    total: int


class PaginatedStoppages(BaseModel):
    data: list[StoppageRead]
    pagination: PaginationMeta
