from datetime import time
import asyncio
import logging

from sqlalchemy import select

from app.core.config import get_settings
from app.core.security import hash_password
from app.db.session import SessionLocal
from app.models.machine import Machine
from app.models.shift import Shift
from app.models.stoppage_reason import MeasurementType, StoppageReason
from app.models.supervisor import Supervisor
from app.models.user import User, UserRole

logger = logging.getLogger("pdms.seed")

SUPERVISORS = [
    "Azhaguvel",
    "Gurunathan",
    "Manimaran",
    "Maniraj",
    "Prakash",
    "Venkatesh",
]

MACHINES = [f"P-{str(i).zfill(2)}" for i in range(1, 30)]

REASONS = [
    ("Equipment Failure", True, "Equipment Failure Detail", MeasurementType.DURATION_MINUTES, None),
    ("Setup Changeover Time", False, None, MeasurementType.DURATION_MINUTES, None),
    (
        "No of Changeover",
        False,
        None,
        MeasurementType.DURATION_MINUTES,
        "TODO: Client confirmation required: whether this field represents duration in minutes or number of occurrences.",
    ),
    ("Tool Problem", True, "Tool Stoppage Details", MeasurementType.DURATION_MINUTES, None),
    ("Adjustment / Minor Stoppage", True, "Details", MeasurementType.DURATION_MINUTES, None),
    ("Coil Changeover", False, None, MeasurementType.DURATION_MINUTES, None),
    (
        "No of Coil Changeover",
        False,
        None,
        MeasurementType.DURATION_MINUTES,
        "TODO: Client confirmation required: whether this field represents duration in minutes or number of occurrences.",
    ),
    ("Scrape Bin Change", False, None, MeasurementType.DURATION_MINUTES, None),
    ("Quality Inspection", False, None, MeasurementType.DURATION_MINUTES, None),
    ("No Operator", False, None, MeasurementType.DURATION_MINUTES, None),
    ("No Material", False, None, MeasurementType.DURATION_MINUTES, None),
    ("Waiting for Tool", False, None, MeasurementType.DURATION_MINUTES, None),
    ("No Plan", False, None, MeasurementType.DURATION_MINUTES, None),
    ("No Power", False, None, MeasurementType.DURATION_MINUTES, None),
    ("Scheduled Cleaning", False, None, MeasurementType.DURATION_MINUTES, None),
    ("Meeting / Training", False, None, MeasurementType.DURATION_MINUTES, None),
    ("Waiting for Forklift / Crane", False, None, MeasurementType.DURATION_MINUTES, None),
    ("Engr improvement / Engineering Improvement", False, None, MeasurementType.DURATION_MINUTES, None),
    ("Coil Issue", False, None, MeasurementType.DURATION_MINUTES, None),
    ("Waiting for Packing Material", False, None, MeasurementType.DURATION_MINUTES, None),
    ("Chute parts running", False, None, MeasurementType.DURATION_MINUTES, None),
]


async def seed() -> None:
    settings = get_settings()
    async with SessionLocal() as db:
        if (await db.execute(select(Supervisor))).scalars().first() is None:
            for name in SUPERVISORS:
                db.add(Supervisor(name=name, active=True))
        if (await db.execute(select(Machine))).scalars().first() is None:
            for code in MACHINES:
                db.add(Machine(code=code, name=code, active=True))
        if (await db.execute(select(Shift))).scalars().first() is None:
            db.add_all(
                [
                    Shift(
                        code="A",
                        name="Shift A",
                        start_time=time(6, 0),
                        end_time=time(14, 0),
                        crosses_midnight=False,
                        sort_order=1,
                    ),
                    Shift(
                        code="B",
                        name="Shift B",
                        start_time=time(14, 0),
                        end_time=time(22, 0),
                        crosses_midnight=False,
                        sort_order=2,
                    ),
                    Shift(
                        code="C",
                        name="Shift C",
                        start_time=time(22, 0),
                        end_time=time(6, 0),
                        crosses_midnight=True,
                        sort_order=3,
                    ),
                ]
            )
        if (await db.execute(select(StoppageReason))).scalars().first() is None:
            for index, (name, requires, label, measurement, notes) in enumerate(REASONS, 1):
                db.add(
                    StoppageReason(
                        name=name,
                        requires_details=requires,
                        details_label=label,
                        measurement_type=measurement,
                        sort_order=index,
                        notes=notes,
                        active=True,
                    )
                )
        if (await db.execute(select(User))).scalars().first() is None:
            if settings.is_production:
                logger.warning("Skipping default user seed in production. Create users explicitly.")
            else:
                db.add(
                    User(
                        username=settings.dev_admin_username,
                        hashed_password=hash_password(settings.dev_admin_password),
                        role=UserRole.ADMIN,
                        is_active=True,
                    )
                )
                db.add(
                    User(
                        username=settings.dev_supervisor_username,
                        hashed_password=hash_password(settings.dev_supervisor_password),
                        role=UserRole.SUPERVISOR,
                        supervisor_id=None,
                        is_active=True,
                    )
                )
        await db.commit()
        logger.info("Master data seed completed")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(seed())
