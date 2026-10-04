import uuid
from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import CheckConstraint, Date, DateTime, ForeignKey, Index, Numeric, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.mixins import TimestampMixin


class StoppageRecord(TimestampMixin, Base):
    __tablename__ = "stoppage_records"
    __table_args__ = (
        CheckConstraint("duration_minutes > 0", name="ck_stoppage_duration_positive"),
        Index("ix_stoppages_production_date", "production_date"),
        Index("ix_stoppages_shift_id", "shift_id"),
        Index("ix_stoppages_supervisor_id", "supervisor_id"),
        Index("ix_stoppages_machine_id", "machine_id"),
        Index("ix_stoppages_reason_id", "stoppage_reason_id"),
        Index("ix_stoppages_created_at", "created_at"),
        Index("ix_stoppages_date_shift", "production_date", "shift_id"),
        Index("ix_stoppages_date_machine", "production_date", "machine_id"),
        Index("ix_stoppages_deleted_at", "deleted_at"),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    production_date: Mapped[date] = mapped_column(Date, nullable=False)
    shift_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("shifts.id"), nullable=False
    )
    supervisor_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("supervisors.id"), nullable=False
    )
    machine_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("machines.id"), nullable=False
    )
    stoppage_reason_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("stoppage_reasons.id"), nullable=False
    )
    duration_minutes: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    details: Mapped[str | None] = mapped_column(Text, nullable=True)
    remarks: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_by: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("users.id"), nullable=True
    )
    updated_by: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("users.id"), nullable=True
    )
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    shift = relationship("Shift")
    supervisor = relationship("Supervisor")
    machine = relationship("Machine")
    reason = relationship("StoppageReason")
    created_by_user = relationship("User", foreign_keys=[created_by])
