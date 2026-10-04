from datetime import date
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field

from app.schemas.stoppage import StoppageRead


class DashboardFilters(BaseModel):
    date_from: date | None = None
    date_to: date | None = None
    shift_id: UUID | None = None
    supervisor_id: UUID | None = None
    machine_id: UUID | None = None
    reason_id: UUID | None = None


class KPISummary(BaseModel):
    total_downtime_minutes: Decimal
    current_shift_downtime_minutes: Decimal
    today_downtime_minutes: Decimal
    total_entries: int
    current_production_date: date
    current_shift_code: str


class NamedTotal(BaseModel):
    id: UUID
    name: str
    downtime_minutes: Decimal
    stoppage_count: int
    average_minutes: Decimal = Decimal("0")


class TrendPoint(BaseModel):
    period: str
    downtime_minutes: Decimal
    stoppage_count: int


class DashboardSummary(BaseModel):
    kpis: KPISummary
    machines: list[NamedTotal]
    reasons: list[NamedTotal]
    shifts: list[NamedTotal]
    daily_trend: list[TrendPoint]
    weekly_trend: list[TrendPoint]
    monthly_trend: list[TrendPoint]
    recent: list[StoppageRead]


class ReportRequest(DashboardFilters):
    format: str = Field(default="excel")
    report_type: str = Field(default="complete")
