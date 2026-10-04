from datetime import date
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import require_authenticated
from app.db.session import get_db
from app.models.user import User
from app.schemas.stoppage import PaginatedStoppages, StoppageCreate, StoppageFilters, StoppageRead, StoppageUpdate
from app.services.stoppage import StoppageService

router = APIRouter(prefix="/stoppages", tags=["Stoppages"])


def filters_from_query(
    date_from: date | None = Query(default=None),
    date_to: date | None = Query(default=None),
    shift_id: UUID | None = Query(default=None),
    supervisor_id: UUID | None = Query(default=None),
    machine_id: UUID | None = Query(default=None),
    reason_id: UUID | None = Query(default=None),
    search: str | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=25, ge=1, le=100),
    sort_by: str = Query(default="created_at"),
    sort_order: str = Query(default="desc"),
) -> StoppageFilters:
    return StoppageFilters(
        date_from=date_from,
        date_to=date_to,
        shift_id=shift_id,
        supervisor_id=supervisor_id,
        machine_id=machine_id,
        reason_id=reason_id,
        search=search,
        page=page,
        page_size=page_size,
        sort_by=sort_by,
        sort_order=sort_order,
    )


@router.get("", response_model=PaginatedStoppages)
async def list_stoppages(
    filters: StoppageFilters = Depends(filters_from_query),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_authenticated),
):
    return await StoppageService(db).list(filters)


@router.post("", response_model=StoppageRead, status_code=201)
async def create_stoppage(
    payload: StoppageCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_authenticated),
):
    return await StoppageService(db).create(payload, user)


@router.get("/{item_id}", response_model=StoppageRead)
async def get_stoppage(
    item_id: UUID,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_authenticated),
):
    return await StoppageService(db).get(item_id)


@router.patch("/{item_id}", response_model=StoppageRead)
async def update_stoppage(
    item_id: UUID,
    payload: StoppageUpdate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_authenticated),
):
    return await StoppageService(db).update(item_id, payload, user)


@router.delete("/{item_id}", status_code=204)
async def delete_stoppage(
    item_id: UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_authenticated),
):
    await StoppageService(db).delete(item_id, user)
