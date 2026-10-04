from datetime import datetime, timezone
from uuid import UUID

from fastapi import Depends, WebSocket
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import AppError
from app.core.security import decode_token
from app.db.session import get_db
from app.models.user import User, UserRole

bearer = HTTPBearer(auto_error=False)


async def get_current_user(
    creds: HTTPAuthorizationCredentials | None = Depends(bearer),
    db: AsyncSession = Depends(get_db),
) -> User:
    if creds is None:
        raise AppError("Please sign in to continue.", status_code=401, code="UNAUTHENTICATED")
    try:
        payload = decode_token(creds.credentials)
        user_id = payload.get("sub")
    except (ValueError, JWTError) as exc:
        raise AppError("Your session has expired. Please sign in again.", status_code=401, code="UNAUTHENTICATED") from exc
    result = await db.execute(select(User).where(User.id == UUID(user_id)))
    user = result.scalar_one_or_none()
    if user is None or not user.is_active:
        raise AppError("Your session is no longer valid.", status_code=401, code="UNAUTHENTICATED")
    return user


async def get_current_user_ws(websocket: WebSocket, db: AsyncSession) -> User | None:
    token = websocket.query_params.get("token")
    if not token:
        return None
    try:
        payload = decode_token(token)
        result = await db.execute(select(User).where(User.id == UUID(payload["sub"])))
        user = result.scalar_one_or_none()
        if user and user.is_active:
            return user
    except Exception:
        return None
    return None


def require_admin(user: User = Depends(get_current_user)) -> User:
    if user.role != UserRole.ADMIN:
        raise AppError("You do not have permission to perform this action.", status_code=403, code="FORBIDDEN")
    return user


def require_authenticated(user: User = Depends(get_current_user)) -> User:
    return user
