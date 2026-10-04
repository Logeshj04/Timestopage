from datetime import date, timedelta
from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.timezone import current_production_context
from app.repositories.dashboard import DashboardRepository
from app.repositories.stoppage import ShiftRepository, StoppageRepository
from app.schemas.dashboard import DashboardSummary, KPISummary
from app.schemas.stoppage import StoppageFilters


class DashboardService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.repo = DashboardRepository(db)
        self.stoppages = StoppageRepository(db)
        self.shifts = ShiftRepository(db)

    def _with_defaults(self, filters: StoppageFilters, today: date) -> StoppageFilters:
        if filters.date_from is None and filters.date_to is None:
            return filters.model_copy(update={"date_from": today, "date_to": today})
        return filters

    async def summary(self, filters: StoppageFilters) -> DashboardSummary:
        production_date, shift_code = current_production_context()
        filters = self._with_defaults(filters, production_date)
        total_minutes, total_count = await self.stoppages.sum_duration(filters)

        today_filters = StoppageFilters(
            date_from=production_date,
            date_to=production_date,
            supervisor_id=filters.supervisor_id,
            machine_id=filters.machine_id,
            reason_id=filters.reason_id,
        )
        today_minutes, _ = await self.stoppages.sum_duration(today_filters)

        current_shift = await self.shifts.get_by_code(shift_code)
        shift_minutes = Decimal("0")
        if current_shift:
            shift_filters = StoppageFilters(
                date_from=production_date,
                date_to=production_date,
                shift_id=current_shift.id,
                supervisor_id=filters.supervisor_id,
                machine_id=filters.machine_id,
                reason_id=filters.reason_id,
            )
            minutes, _ = await self.stoppages.sum_duration(shift_filters)
            shift_minutes = Decimal(str(minutes))

        recent = await self.stoppages.recent()
        return DashboardSummary(
            kpis=KPISummary(
                total_downtime_minutes=Decimal(str(total_minutes)),
                current_shift_downtime_minutes=shift_minutes,
                today_downtime_minutes=Decimal(str(today_minutes)),
                total_entries=total_count,
                current_production_date=production_date,
                current_shift_code=shift_code,
            ),
            machines=await self.repo.machine_totals(filters),
            reasons=await self.repo.reason_totals(filters),
            shifts=await self.repo.shift_totals(filters),
            daily_trend=await self.repo.daily_trend(filters),
            weekly_trend=await self.repo.weekly_trend(filters),
            monthly_trend=await self.repo.monthly_trend(filters),
            recent=recent,
        )
