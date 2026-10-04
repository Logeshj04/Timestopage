from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import AppError
from app.core.rate_limit import login_attempts
from app.core.security import create_access_token, hash_password, verify_password
from app.models.user import User, UserRole
from app.repositories.stoppage import UserRepository
from app.schemas.user import UserCreate, UserUpdate


class AuthService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.users = UserRepository(db)

    async def authenticate(self, username: str, password: str, client_key: str) -> str:
        login_attempts.check(client_key)
        user = await self.users.get_by_username(username)
        if user is None or not user.is_active or not verify_password(password, user.hashed_password):
            login_attempts.record_failure(client_key)
            raise AppError("Invalid username or password.", status_code=401, code="INVALID_CREDENTIALS")
        login_attempts.reset(client_key)
        return create_access_token(str(user.id), extra={"role": user.role.value})

    async def list_users(self) -> list[User]:
        return list(await self.users.list_all())

    async def create_user(self, payload: UserCreate) -> User:
        existing = await self.users.get_by_username(payload.username)
        if existing:
            raise AppError("A user with this username already exists.", status_code=409, code="DUPLICATE")
        user = User(
            username=payload.username.strip(),
            hashed_password=hash_password(payload.password),
            role=payload.role,
            supervisor_id=payload.supervisor_id,
            is_active=payload.is_active,
        )
        await self.users.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def update_user(self, user_id: UUID, payload: UserUpdate) -> User:
        user = await self.users.get(user_id)
        if user is None:
            raise AppError("User was not found.", status_code=404, code="NOT_FOUND")
        data = payload.model_dump(exclude_unset=True)
        if "password" in data and data["password"]:
            user.hashed_password = hash_password(data.pop("password"))
        else:
            data.pop("password", None)
        for key, value in data.items():
            setattr(user, key, value)
        await self.db.commit()
        await self.db.refresh(user)
        return user
