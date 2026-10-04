from uuid import UUID

from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user, require_admin
from app.db.session import get_db
from app.models.user import User
from app.schemas.user import LoginRequest, TokenResponse, UserCreate, UserRead, UserUpdate
from app.services.auth import AuthService

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/login", response_model=TokenResponse)
async def login(payload: LoginRequest, request: Request, db: AsyncSession = Depends(get_db)):
    service = AuthService(db)
    client_key = request.client.host if request.client else "unknown"
    token = await service.authenticate(payload.username, payload.password, client_key)
    return TokenResponse(access_token=token)


@router.get("/me", response_model=UserRead)
async def me(user: User = Depends(get_current_user)):
    return user


@router.get("/users", response_model=list[UserRead])
async def list_users(db: AsyncSession = Depends(get_db), _: User = Depends(require_admin)):
    return await AuthService(db).list_users()


@router.post("/users", response_model=UserRead, status_code=201)
async def create_user(payload: UserCreate, db: AsyncSession = Depends(get_db), _: User = Depends(require_admin)):
    return await AuthService(db).create_user(payload)


@router.patch("/users/{user_id}", response_model=UserRead)
async def update_user(
    user_id: UUID,
    payload: UserUpdate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_admin),
):
    return await AuthService(db).update_user(user_id, payload)
