from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import AppError
from app.models.stoppage import StoppageRecord
from app.models.user import User, UserRole
from app.repositories.stoppage import (
    MachineRepository,
    ReasonRepository,
    ShiftRepository,
    StoppageRepository,
    SupervisorRepository,
)
from app.schemas.stoppage import PaginatedStoppages, PaginationMeta, StoppageCreate, StoppageFilters, StoppageUpdate
from app.websocket.events import publish_stoppage_event


class StoppageService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.repo = StoppageRepository(db)
        self.shifts = ShiftRepository(db)
        self.supervisors = SupervisorRepository(db)
        self.machines = MachineRepository(db)
        self.reasons = ReasonRepository(db)

    def can_mutate(self, user: User, record: StoppageRecord) -> bool:
        if user.role == UserRole.ADMIN:
            return True
        if user.supervisor_id is not None:
            return record.supervisor_id == user.supervisor_id
        return record.created_by == user.id

    async def _require_active_masters(self, payload: StoppageCreate | StoppageUpdate, existing: StoppageRecord | None = None) -> None:
        data = payload.model_dump(exclude_unset=True)
        shift_id = data.get("shift_id", existing.shift_id if existing else None)
        supervisor_id = data.get("supervisor_id", existing.supervisor_id if existing else None)
        machine_id = data.get("machine_id", existing.machine_id if existing else None)
        reason_id = data.get("stoppage_reason_id", existing.stoppage_reason_id if existing else None)

        shift = await self.shifts.get(shift_id)
        if shift is None or not shift.active:
            raise AppError("Please select a valid shift.", status_code=400, code="VALIDATION_ERROR")
        supervisor = await self.supervisors.get(supervisor_id)
        if supervisor is None or not supervisor.active:
            raise AppError("Please select a valid supervisor.", status_code=400, code="VALIDATION_ERROR")
        machine = await self.machines.get(machine_id)
        if machine is None or not machine.active:
            raise AppError("Please select a valid machine.", status_code=400, code="VALIDATION_ERROR")
        reason = await self.reasons.get(reason_id)
        if reason is None or not reason.active:
            raise AppError("Please select a valid stoppage reason.", status_code=400, code="VALIDATION_ERROR")

    async def create(self, payload: StoppageCreate, user: User) -> StoppageRecord:
        await self._require_active_masters(payload)
        record = StoppageRecord(
            **payload.model_dump(),
            created_by=user.id,
            updated_by=user.id,
        )
        await self.repo.add(record)
        await self.db.commit()
        created = await self.repo.get_with_relations(record.id)
        await publish_stoppage_event("stoppage.created", created.id)
        return created

    async def list(self, filters: StoppageFilters) -> PaginatedStoppages:
        rows, total = await self.repo.list_filtered(filters)
        return PaginatedStoppages(
            data=rows,
            pagination=PaginationMeta(page=filters.page, page_size=filters.page_size, total=total),
        )

    async def get(self, item_id: UUID) -> StoppageRecord:
        record = await self.repo.get_with_relations(item_id)
        if record is None:
            raise AppError("Stoppage record was not found.", status_code=404, code="NOT_FOUND")
        return record

    async def update(self, item_id: UUID, payload: StoppageUpdate, user: User) -> StoppageRecord:
        record = await self.get(item_id)
        if not self.can_mutate(user, record):
            raise AppError("You can only edit your own stoppage records.", status_code=403, code="FORBIDDEN")
        await self._require_active_masters(payload, record)
        for key, value in payload.model_dump(exclude_unset=True).items():
            setattr(record, key, value)
        record.updated_by = user.id
        await self.db.commit()
        updated = await self.repo.get_with_relations(record.id)
        await publish_stoppage_event("stoppage.updated", updated.id)
        return updated

    async def delete(self, item_id: UUID, user: User) -> None:
        record = await self.get(item_id)
        if not self.can_mutate(user, record):
            raise AppError("You can only delete your own stoppage records.", status_code=403, code="FORBIDDEN")
        record.deleted_at = datetime.now(timezone.utc)
        record.updated_by = user.id
        await self.db.commit()
        await publish_stoppage_event("stoppage.deleted", record.id)
