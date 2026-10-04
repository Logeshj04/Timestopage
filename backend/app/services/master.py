from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import AppError
from app.models.machine import Machine
from app.models.shift import Shift
from app.models.stoppage_reason import StoppageReason
from app.models.supervisor import Supervisor
from app.repositories.stoppage import (
    MachineRepository,
    ReasonRepository,
    ShiftRepository,
    SupervisorRepository,
)


class MasterDataService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.supervisors = SupervisorRepository(db)
        self.machines = MachineRepository(db)
        self.shifts = ShiftRepository(db)
        self.reasons = ReasonRepository(db)

    async def _create(self, repo, model, payload):
        instance = model(**payload.model_dump())
        await repo.add(instance)
        await self.db.commit()
        await self.db.refresh(instance)
        return instance

    async def _update(self, repo, item_id: UUID, payload, label: str):
        instance = await repo.get(item_id)
        if instance is None:
            raise AppError(f"{label} was not found.", status_code=404, code="NOT_FOUND")
        for key, value in payload.model_dump(exclude_unset=True).items():
            setattr(instance, key, value)
        await self.db.commit()
        await self.db.refresh(instance)
        return instance

    async def list_supervisors(self, active_only: bool = False):
        return await self.supervisors.list_all(active_only=active_only)

    async def create_supervisor(self, payload):
        return await self._create(self.supervisors, Supervisor, payload)

    async def update_supervisor(self, item_id: UUID, payload):
        return await self._update(self.supervisors, item_id, payload, "Supervisor")

    async def list_machines(self, active_only: bool = False):
        return await self.machines.list_all(active_only=active_only)

    async def create_machine(self, payload):
        return await self._create(self.machines, Machine, payload)

    async def update_machine(self, item_id: UUID, payload):
        return await self._update(self.machines, item_id, payload, "Machine")

    async def list_shifts(self, active_only: bool = False):
        return await self.shifts.list_all(active_only=active_only)

    async def create_shift(self, payload):
        return await self._create(self.shifts, Shift, payload)

    async def update_shift(self, item_id: UUID, payload):
        return await self._update(self.shifts, item_id, payload, "Shift")

    async def list_reasons(self, active_only: bool = False):
        return await self.reasons.list_all(active_only=active_only)

    async def create_reason(self, payload):
        return await self._create(self.reasons, StoppageReason, payload)

    async def update_reason(self, item_id: UUID, payload):
        return await self._update(self.reasons, item_id, payload, "Stoppage reason")
