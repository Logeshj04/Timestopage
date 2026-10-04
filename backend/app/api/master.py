from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import require_admin, require_authenticated
from app.db.session import get_db
from app.models.user import User
from app.schemas.master import (
    MachineCreate,
    MachineRead,
    MachineUpdate,
    ReasonCreate,
    ReasonRead,
    ReasonUpdate,
    ShiftCreate,
    ShiftRead,
    ShiftUpdate,
    SupervisorCreate,
    SupervisorRead,
    SupervisorUpdate,
)
from app.services.master import MasterDataService

router = APIRouter(tags=["Master data"])


def service(db: AsyncSession = Depends(get_db)) -> MasterDataService:
    return MasterDataService(db)


@router.get("/supervisors", response_model=list[SupervisorRead])
async def list_supervisors(
    active_only: bool = Query(default=False),
    svc: MasterDataService = Depends(service),
    _: User = Depends(require_authenticated),
):
    return await svc.list_supervisors(active_only)


@router.post("/supervisors", response_model=SupervisorRead, status_code=201)
async def create_supervisor(
    payload: SupervisorCreate,
    svc: MasterDataService = Depends(service),
    _: User = Depends(require_admin),
):
    return await svc.create_supervisor(payload)


@router.patch("/supervisors/{item_id}", response_model=SupervisorRead)
async def update_supervisor(
    item_id: UUID,
    payload: SupervisorUpdate,
    svc: MasterDataService = Depends(service),
    _: User = Depends(require_admin),
):
    return await svc.update_supervisor(item_id, payload)


@router.get("/machines", response_model=list[MachineRead])
async def list_machines(
    active_only: bool = Query(default=False),
    svc: MasterDataService = Depends(service),
    _: User = Depends(require_authenticated),
):
    return await svc.list_machines(active_only)


@router.post("/machines", response_model=MachineRead, status_code=201)
async def create_machine(
    payload: MachineCreate,
    svc: MasterDataService = Depends(service),
    _: User = Depends(require_admin),
):
    return await svc.create_machine(payload)


@router.patch("/machines/{item_id}", response_model=MachineRead)
async def update_machine(
    item_id: UUID,
    payload: MachineUpdate,
    svc: MasterDataService = Depends(service),
    _: User = Depends(require_admin),
):
    return await svc.update_machine(item_id, payload)


@router.get("/shifts", response_model=list[ShiftRead])
async def list_shifts(
    active_only: bool = Query(default=False),
    svc: MasterDataService = Depends(service),
    _: User = Depends(require_authenticated),
):
    return await svc.list_shifts(active_only)


@router.post("/shifts", response_model=ShiftRead, status_code=201)
async def create_shift(
    payload: ShiftCreate,
    svc: MasterDataService = Depends(service),
    _: User = Depends(require_admin),
):
    return await svc.create_shift(payload)


@router.patch("/shifts/{item_id}", response_model=ShiftRead)
async def update_shift(
    item_id: UUID,
    payload: ShiftUpdate,
    svc: MasterDataService = Depends(service),
    _: User = Depends(require_admin),
):
    return await svc.update_shift(item_id, payload)


@router.get("/stoppage-reasons", response_model=list[ReasonRead])
async def list_reasons(
    active_only: bool = Query(default=False),
    svc: MasterDataService = Depends(service),
    _: User = Depends(require_authenticated),
):
    return await svc.list_reasons(active_only)


@router.post("/stoppage-reasons", response_model=ReasonRead, status_code=201)
async def create_reason(
    payload: ReasonCreate,
    svc: MasterDataService = Depends(service),
    _: User = Depends(require_admin),
):
    return await svc.create_reason(payload)


@router.patch("/stoppage-reasons/{item_id}", response_model=ReasonRead)
async def update_reason(
    item_id: UUID,
    payload: ReasonUpdate,
    svc: MasterDataService = Depends(service),
    _: User = Depends(require_admin),
):
    return await svc.update_reason(item_id, payload)
