from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.exceptions import AppError
from app.reports.excel import build_workbook, format_filters
from app.reports.pdf import build_pdf
from app.repositories.dashboard import DashboardRepository
from app.repositories.stoppage import StoppageRepository
from app.schemas.stoppage import StoppageFilters
from app.services.dashboard import DashboardService


class ReportService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.stoppages = StoppageRepository(db)
        self.dashboard = DashboardRepository(db)
        self.summary_service = DashboardService(db)

    def _filter_text(self, filters: StoppageFilters) -> str:
        return format_filters(
            {
                "date_from": filters.date_from,
                "date_to": filters.date_to,
                "shift_id": filters.shift_id,
                "supervisor_id": filters.supervisor_id,
                "machine_id": filters.machine_id,
                "reason_id": filters.reason_id,
                "search": filters.search,
            }
        )

    def _named_rows(self, items) -> list[tuple]:
        return [(item.name, item.downtime_minutes, item.stoppage_count) for item in items]

    async def _dataset(self, filters: StoppageFilters):
        settings = get_settings()
        records = await self.stoppages.list_for_export(filters, settings.report_max_rows)
        if not records:
            raise AppError(
                "No records found for the selected filters.",
                status_code=404,
                code="NO_RECORDS",
            )
        if len(records) >= settings.report_max_rows:
            raise AppError(
                "Too many records for export. Please narrow the date range or filters.",
                status_code=400,
                code="EXPORT_TOO_LARGE",
            )
        summaries = {
            "machines": self._named_rows(await self.dashboard.machine_totals(filters)),
            "reasons": self._named_rows(await self.dashboard.reason_totals(filters)),
            "shifts": self._named_rows(await self.dashboard.shift_totals(filters)),
            "daily": [
                (point.period, point.downtime_minutes, point.stoppage_count)
                for point in await self.dashboard.daily_trend(filters)
            ],
        }
        return records, summaries

    async def excel(self, filters: StoppageFilters, report_type: str) -> Response:
        if report_type not in {"raw", "summary", "complete"}:
            raise AppError("Unknown Excel report type.", status_code=400, code="VALIDATION_ERROR")
        records, summaries = await self._dataset(filters)
        content = build_workbook(report_type, records, summaries, self._filter_text(filters))
        filename = f"downtime-{report_type}.xlsx"
        return Response(
            content=content,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f'attachment; filename="{filename}"'},
        )

    async def pdf(self, filters: StoppageFilters) -> Response:
        records, summaries = await self._dataset(filters)
        dashboard = await self.summary_service.summary(filters)
        content = build_pdf(
            records,
            summaries,
            {
                "total_downtime": dashboard.kpis.total_downtime_minutes,
                "total_entries": dashboard.kpis.total_entries,
                "production_date": dashboard.kpis.current_production_date.isoformat(),
                "shift_code": dashboard.kpis.current_shift_code,
            },
            self._filter_text(filters),
        )
        return Response(
            content=content,
            media_type="application/pdf",
            headers={"Content-Disposition": 'attachment; filename="downtime-report.pdf"'},
        )
