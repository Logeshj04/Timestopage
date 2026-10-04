from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.machine import Machine
from app.models.shift import Shift
from app.models.stoppage import StoppageRecord
from app.models.stoppage_reason import StoppageReason
from app.models.supervisor import Supervisor
from app.repositories.stoppage import apply_stoppage_filters
from app.schemas.dashboard import NamedTotal, TrendPoint
from app.schemas.stoppage import StoppageFilters


def _named(row) -> NamedTotal:
    downtime = Decimal(str(row.downtime or 0))
    count = int(row.count or 0)
    average = (downtime / count) if count else Decimal("0")
    return NamedTotal(
        id=row.id,
        name=row.name,
        downtime_minutes=downtime,
        stoppage_count=count,
        average_minutes=average,
    )


class DashboardRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    def _joins(self, stmt):
        return stmt.join(Machine).join(Supervisor).join(StoppageReason).join(Shift)

    def _dialect(self) -> str:
        bind = self.db.bind
        return bind.dialect.name if bind is not None else "postgresql"

    def _week_expr(self):
        if self._dialect() == "sqlite":
            return func.strftime("%Y-%W", StoppageRecord.production_date)
        return func.to_char(StoppageRecord.production_date, "IYYY-IW")

    def _month_expr(self):
        if self._dialect() == "sqlite":
            return func.strftime("%Y-%m", StoppageRecord.production_date)
        return func.to_char(StoppageRecord.production_date, "YYYY-MM")

    async def machine_totals(self, filters: StoppageFilters) -> list[NamedTotal]:
        stmt = apply_stoppage_filters(
            self._joins(
                select(
                    Machine.id.label("id"),
                    Machine.code.label("name"),
                    func.coalesce(func.sum(StoppageRecord.duration_minutes), 0).label("downtime"),
                    func.count(StoppageRecord.id).label("count"),
                )
            )
            .group_by(Machine.id, Machine.code)
            .order_by(func.coalesce(func.sum(StoppageRecord.duration_minutes), 0).desc()),
            filters,
        )
        rows = (await self.db.execute(stmt)).all()
        return [_named(row) for row in rows]

    async def reason_totals(self, filters: StoppageFilters) -> list[NamedTotal]:
        stmt = apply_stoppage_filters(
            self._joins(
                select(
                    StoppageReason.id.label("id"),
                    StoppageReason.name.label("name"),
                    func.coalesce(func.sum(StoppageRecord.duration_minutes), 0).label("downtime"),
                    func.count(StoppageRecord.id).label("count"),
                )
            )
            .group_by(StoppageReason.id, StoppageReason.name)
            .order_by(func.coalesce(func.sum(StoppageRecord.duration_minutes), 0).desc()),
            filters,
        )
        rows = (await self.db.execute(stmt)).all()
        return [_named(row) for row in rows]

    async def shift_totals(self, filters: StoppageFilters) -> list[NamedTotal]:
        stmt = apply_stoppage_filters(
            self._joins(
                select(
                    Shift.id.label("id"),
                    Shift.code.label("name"),
                    func.coalesce(func.sum(StoppageRecord.duration_minutes), 0).label("downtime"),
                    func.count(StoppageRecord.id).label("count"),
                )
            )
            .group_by(Shift.id, Shift.code, Shift.sort_order)
            .order_by(Shift.sort_order),
            filters,
        )
        rows = (await self.db.execute(stmt)).all()
        return [_named(row) for row in rows]

    async def daily_trend(self, filters: StoppageFilters) -> list[TrendPoint]:
        stmt = apply_stoppage_filters(
            self._joins(
                select(
                    StoppageRecord.production_date.label("period"),
                    func.coalesce(func.sum(StoppageRecord.duration_minutes), 0).label("downtime"),
                    func.count(StoppageRecord.id).label("count"),
                )
            )
            .group_by(StoppageRecord.production_date)
            .order_by(StoppageRecord.production_date),
            filters,
        )
        rows = (await self.db.execute(stmt)).all()
        return [
            TrendPoint(
                period=row.period.isoformat(),
                downtime_minutes=Decimal(str(row.downtime or 0)),
                stoppage_count=int(row.count or 0),
            )
            for row in rows
        ]

    async def weekly_trend(self, filters: StoppageFilters) -> list[TrendPoint]:
        week = self._week_expr()
        stmt = apply_stoppage_filters(
            self._joins(
                select(
                    week.label("period"),
                    func.coalesce(func.sum(StoppageRecord.duration_minutes), 0).label("downtime"),
                    func.count(StoppageRecord.id).label("count"),
                )
            )
            .group_by(week)
            .order_by(week),
            filters,
        )
        rows = (await self.db.execute(stmt)).all()
        return [
            TrendPoint(
                period=str(row.period),
                downtime_minutes=Decimal(str(row.downtime or 0)),
                stoppage_count=int(row.count or 0),
            )
            for row in rows
        ]

    async def monthly_trend(self, filters: StoppageFilters) -> list[TrendPoint]:
        month = self._month_expr()
        stmt = apply_stoppage_filters(
            self._joins(
                select(
                    month.label("period"),
                    func.coalesce(func.sum(StoppageRecord.duration_minutes), 0).label("downtime"),
                    func.count(StoppageRecord.id).label("count"),
                )
            )
            .group_by(month)
            .order_by(month),
            filters,
        )
        rows = (await self.db.execute(stmt)).all()
        return [
            TrendPoint(
                period=str(row.period),
                downtime_minutes=Decimal(str(row.downtime or 0)),
                stoppage_count=int(row.count or 0),
            )
            for row in rows
        ]
