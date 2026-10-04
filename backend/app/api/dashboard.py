from datetime import date
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import require_authenticated
from app.db.session import get_db
from app.models.user import User
from app.reports.service import ReportService
from app.schemas.dashboard import DashboardSummary
from app.schemas.stoppage import StoppageFilters
from app.services.dashboard import DashboardService

router = APIRouter(tags=["Dashboard and reports"])


def dashboard_filters(
    date_from: date | None = Query(default=None),
    date_to: date | None = Query(default=None),
    shift_id: UUID | None = Query(default=None),
    supervisor_id: UUID | None = Query(default=None),
    machine_id: UUID | None = Query(default=None),
    reason_id: UUID | None = Query(default=None),
) -> StoppageFilters:
    return StoppageFilters(
        date_from=date_from,
        date_to=date_to,
        shift_id=shift_id,
        supervisor_id=supervisor_id,
        machine_id=machine_id,
        reason_id=reason_id,
        page=1,
        page_size=100,
    )


@router.get("/dashboard/summary", response_model=DashboardSummary)
async def dashboard_summary(
    filters: StoppageFilters = Depends(dashboard_filters),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_authenticated),
):
    return await DashboardService(db).summary(filters)


@router.get("/reports/excel")
async def excel_report(
    report_type: str = Query(default="complete"),
    filters: StoppageFilters = Depends(dashboard_filters),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_authenticated),
):
    return await ReportService(db).excel(filters, report_type)


@router.get("/reports/pdf")
async def pdf_report(
    filters: StoppageFilters = Depends(dashboard_filters),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_authenticated),
):
    return await ReportService(db).pdf(filters)
