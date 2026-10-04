from datetime import date
from decimal import Decimal
from uuid import uuid4

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.security import hash_password
from app.core.timezone import current_production_context, current_production_date, current_shift_code
from app.db.base import Base
from app.db.session import get_db
from app.main import app
from app.models.machine import Machine
from app.models.shift import Shift
from app.models.stoppage_reason import StoppageReason
from app.models.supervisor import Supervisor
from app.models.user import User, UserRole
from datetime import datetime, time, timedelta
from zoneinfo import ZoneInfo


@pytest.fixture
async def session():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    factory = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
    async with factory() as db:
        yield db
    await engine.dispose()


@pytest.fixture
async def client(session: AsyncSession):
    tz = ZoneInfo("Asia/Kolkata")
    shift_a = Shift(code="A", name="Shift A", start_time=time(6, 0), end_time=time(14, 0), sort_order=1)
    shift_b = Shift(code="B", name="Shift B", start_time=time(14, 0), end_time=time(22, 0), sort_order=2)
    shift_c = Shift(
        code="C",
        name="Shift C",
        start_time=time(22, 0),
        end_time=time(6, 0),
        crosses_midnight=True,
        sort_order=3,
    )
    sup_a = Supervisor(name="Supervisor A")
    sup_b = Supervisor(name="Supervisor B")
    machine1 = Machine(code="P-01")
    machine2 = Machine(code="P-02")
    machine3 = Machine(code="P-03")
    machine5 = Machine(code="P-05")
    reason = StoppageReason(name="Equipment Failure", requires_details=True, details_label="Equipment Failure Detail")
    admin = User(username="admin", hashed_password=hash_password("AdminPass123!"), role=UserRole.ADMIN)
    user_a = User(
        username="supera",
        hashed_password=hash_password("SuperPass123!"),
        role=UserRole.SUPERVISOR,
        supervisor_id=None,
    )
    session.add_all([shift_a, shift_b, shift_c, sup_a, sup_b, machine1, machine2, machine3, machine5, reason, admin, user_a])
    await session.commit()
    await session.refresh(sup_a)
    await session.refresh(sup_b)
    user_a.supervisor_id = sup_a.id
    user_b = User(
        username="superb",
        hashed_password=hash_password("SuperPass123!"),
        role=UserRole.SUPERVISOR,
        supervisor_id=sup_b.id,
    )
    session.add(user_b)
    await session.commit()

    async def override_db():
        yield session

    app.dependency_overrides[get_db] = override_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as async_client:
        async_client.shift_a = shift_a  # type: ignore[attr-defined]
        async_client.shift_c = shift_c  # type: ignore[attr-defined]
        async_client.sup_a = sup_a  # type: ignore[attr-defined]
        async_client.sup_b = sup_b  # type: ignore[attr-defined]
        async_client.machine1 = machine1  # type: ignore[attr-defined]
        async_client.machine2 = machine2  # type: ignore[attr-defined]
        async_client.machine3 = machine3  # type: ignore[attr-defined]
        async_client.machine5 = machine5  # type: ignore[attr-defined]
        async_client.reason = reason  # type: ignore[attr-defined]
        yield async_client
    app.dependency_overrides.clear()


async def login(client: AsyncClient, username: str, password: str) -> str:
    response = await client.post("/api/auth/login", json={"username": username, "password": password})
    assert response.status_code == 200, response.text
    return response.json()["access_token"]


def payload(client, **overrides):
    body = {
        "production_date": "2026-08-28",
        "shift_id": str(client.shift_c.id),
        "supervisor_id": str(client.sup_a.id),
        "machine_id": str(client.machine5.id),
        "stoppage_reason_id": str(client.reason.id),
        "duration_minutes": 10,
        "details": "Motor problem",
        "remarks": "Test",
    }
    body.update(overrides)
    return body
