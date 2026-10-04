from collections.abc import Sequence
from typing import Any
from uuid import UUID

from sqlalchemy import Select, func, select
from sqlalchemy.ext.asyncio import AsyncSession


class BaseRepository:
    def __init__(self, db: AsyncSession, model: type) -> None:
        self.db = db
        self.model = model

    async def get(self, item_id: UUID) -> Any:
        result = await self.db.execute(select(self.model).where(self.model.id == item_id))
        return result.scalar_one_or_none()

    async def list_all(self, active_only: bool = False) -> Sequence[Any]:
        stmt: Select = select(self.model)
        if active_only and hasattr(self.model, "active"):
            stmt = stmt.where(self.model.active.is_(True))
        if hasattr(self.model, "sort_order"):
            stmt = stmt.order_by(self.model.sort_order, self.model.name if hasattr(self.model, "name") else self.model.code)
        elif hasattr(self.model, "code"):
            stmt = stmt.order_by(self.model.code)
        elif hasattr(self.model, "name"):
            stmt = stmt.order_by(self.model.name)
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def add(self, instance: Any) -> Any:
        self.db.add(instance)
        await self.db.flush()
        await self.db.refresh(instance)
        return instance

    async def delete(self, instance: Any) -> None:
        await self.db.delete(instance)

    async def count(self) -> int:
        result = await self.db.execute(select(func.count()).select_from(self.model))
        return int(result.scalar_one())
