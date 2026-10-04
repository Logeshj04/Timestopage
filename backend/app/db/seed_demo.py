"""Optional development/demo stoppage records. Never run in production."""

import asyncio
import logging
from datetime import date, timedelta
from decimal import Decimal

from sqlalchemy import select

from app.core.config import get_settings
from app.core.timezone import current_production_date
from app.db.session import SessionLocal
from app.models.machine import Machine
from app.models.shift import Shift
from app.models.stoppage import StoppageRecord
from app.models.stoppage_reason import StoppageReason
from app.models.supervisor import Supervisor
from app.models.user import User

logger = logging.getLogger("pdms.seed_demo")


async def seed_demo() -> None:
    settings = get_settings()
    if settings.is_production:
        raise RuntimeError("Demo stoppage seed is not allowed in production.")
    async with SessionLocal() as db:
        if (await db.execute(select(StoppageRecord))).scalars().first() is not None:
            logger.info("Stoppage records already exist; skipping demo seed")
            return
        machines = (await db.execute(select(Machine).order_by(Machine.code))).scalars().all()
        shifts = (await db.execute(select(Shift).order_by(Shift.sort_order))).scalars().all()
        reasons = (await db.execute(select(StoppageReason).order_by(StoppageReason.sort_order))).scalars().all()
        supervisors = (await db.execute(select(Supervisor).order_by(Supervisor.name))).scalars().all()
        admin = (await db.execute(select(User).where(User.username == settings.dev_admin_username))).scalar_one()
        today = current_production_date()
        samples = [
            (today, 0, 0, 0, 0, 10),
            (today, 0, 0, 0, 0, 15),
            (today, 1, 1, 3, 1, 20),
            (today - timedelta(days=1), 2, 2, 4, 2, 30),
            (today, 1, 2, 10, 3, 50),
        ]
        for prod_date, machine_i, shift_i, reason_i, supervisor_i, minutes in samples:
            db.add(
                StoppageRecord(
                    production_date=prod_date,
                    shift_id=shifts[shift_i].id,
                    supervisor_id=supervisors[supervisor_i].id,
                    machine_id=machines[machine_i].id,
                    stoppage_reason_id=reasons[reason_i].id,
                    duration_minutes=Decimal(minutes),
                    details="Demo detail" if reasons[reason_i].requires_details else None,
                    remarks="Development demo record",
                    created_by=admin.id,
                    updated_by=admin.id,
                )
            )
        await db.commit()
        logger.info("Demo stoppage seed completed")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(seed_demo())
