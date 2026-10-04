from datetime import date
from uuid import UUID

from sqlalchemy import Select, and_, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.machine import Machine
from app.models.shift import Shift
from app.models.stoppage import StoppageRecord
from app.models.stoppage_reason import StoppageReason
from app.models.supervisor import Supervisor
from app.models.user import User
from app.repositories.base import BaseRepository
from app.schemas.stoppage import StoppageFilters


class UserRepository(BaseRepository):
    def __init__(self, db: AsyncSession) -> None:
        super().__init__(db, User)

    async def get_by_username(self, username: str) -> User | None:
        result = await self.db.execute(select(User).where(func.lower(User.username) == username.lower()))
        return result.scalar_one_or_none()


class SupervisorRepository(BaseRepository):
    def __init__(self, db: AsyncSession) -> None:
        super().__init__(db, Supervisor)


class MachineRepository(BaseRepository):
    def __init__(self, db: AsyncSession) -> None:
        super().__init__(db, Machine)


class ShiftRepository(BaseRepository):
    def __init__(self, db: AsyncSession) -> None:
        super().__init__(db, Shift)

    async def get_by_code(self, code: str) -> Shift | None:
        result = await self.db.execute(select(Shift).where(Shift.code == code))
        return result.scalar_one_or_none()


class ReasonRepository(BaseRepository):
    def __init__(self, db: AsyncSession) -> None:
        super().__init__(db, StoppageReason)


def apply_stoppage_filters(stmt: Select, filters: StoppageFilters) -> Select:
    stmt = stmt.where(StoppageRecord.deleted_at.is_(None))
    if filters.date_from:
        stmt = stmt.where(StoppageRecord.production_date >= filters.date_from)
    if filters.date_to:
        stmt = stmt.where(StoppageRecord.production_date <= filters.date_to)
    if filters.shift_id:
        stmt = stmt.where(StoppageRecord.shift_id == filters.shift_id)
    if filters.supervisor_id:
        stmt = stmt.where(StoppageRecord.supervisor_id == filters.supervisor_id)
    if filters.machine_id:
        stmt = stmt.where(StoppageRecord.machine_id == filters.machine_id)
    if filters.reason_id:
        stmt = stmt.where(StoppageRecord.stoppage_reason_id == filters.reason_id)
    if filters.search:
        term = f"%{filters.search.strip().lower()}%"
        stmt = stmt.where(
            or_(
                func.lower(Machine.code).like(term),
                func.lower(Supervisor.name).like(term),
                func.lower(StoppageReason.name).like(term),
                func.lower(func.coalesce(StoppageRecord.details, "")).like(term),
                func.lower(func.coalesce(StoppageRecord.remarks, "")).like(term),
            )
        )
    return stmt


def stoppage_options() -> list:
    return [
        selectinload(StoppageRecord.shift),
        selectinload(StoppageRecord.supervisor),
        selectinload(StoppageRecord.machine),
        selectinload(StoppageRecord.reason),
    ]


class StoppageRepository(BaseRepository):
    def __init__(self, db: AsyncSession) -> None:
        super().__init__(db, StoppageRecord)

    def _base(self) -> Select:
        return (
            select(StoppageRecord)
            .join(Machine)
            .join(Supervisor)
            .join(StoppageReason)
            .join(Shift)
            .options(*stoppage_options())
        )

    async def get_with_relations(self, item_id: UUID) -> StoppageRecord | None:
        stmt = self._base().where(StoppageRecord.id == item_id, StoppageRecord.deleted_at.is_(None))
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def list_filtered(self, filters: StoppageFilters) -> tuple[list[StoppageRecord], int]:
        stmt = apply_stoppage_filters(self._base(), filters)
        count_stmt = apply_stoppage_filters(
            select(func.count(StoppageRecord.id)).join(Machine).join(Supervisor).join(StoppageReason).join(Shift),
            filters,
        )
        total = int((await self.db.execute(count_stmt)).scalar_one())
        sort_map = {
            "production_date": StoppageRecord.production_date,
            "created_at": StoppageRecord.created_at,
            "duration_minutes": StoppageRecord.duration_minutes,
            "machine": Machine.code,
        }
        sort_col = sort_map.get(filters.sort_by, StoppageRecord.created_at)
        order = sort_col.asc() if filters.sort_order == "asc" else sort_col.desc()
        stmt = stmt.order_by(order, StoppageRecord.id.desc())
        stmt = stmt.offset((filters.page - 1) * filters.page_size).limit(filters.page_size)
        rows = (await self.db.execute(stmt)).scalars().unique().all()
        return list(rows), total

    async def list_for_export(self, filters: StoppageFilters, limit: int) -> list[StoppageRecord]:
        export_filters = filters.model_copy(update={"page": 1, "page_size": limit, "sort_by": "production_date", "sort_order": "asc"})
        stmt = apply_stoppage_filters(self._base(), export_filters)
        stmt = stmt.order_by(StoppageRecord.production_date, Shift.sort_order, Machine.code, StoppageRecord.created_at)
        stmt = stmt.limit(limit)
        return list((await self.db.execute(stmt)).scalars().unique().all())

    async def recent(self, limit: int = 12) -> list[StoppageRecord]:
        stmt = (
            select(StoppageRecord)
            .options(*stoppage_options())
            .where(StoppageRecord.deleted_at.is_(None))
            .order_by(StoppageRecord.created_at.desc())
            .limit(limit)
        )
        return list((await self.db.execute(stmt)).scalars().unique().all())

    async def sum_duration(self, filters: StoppageFilters) -> tuple[float, int]:
        stmt = apply_stoppage_filters(
            select(
                func.coalesce(func.sum(StoppageRecord.duration_minutes), 0),
                func.count(StoppageRecord.id),
            )
            .join(Machine)
            .join(Supervisor)
            .join(StoppageReason)
            .join(Shift),
            filters,
        )
        row = (await self.db.execute(stmt)).one()
        return float(row[0] or 0), int(row[1] or 0)
