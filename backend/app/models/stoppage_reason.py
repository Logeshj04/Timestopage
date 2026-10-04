import uuid

from sqlalchemy import Boolean, Integer, String, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.mixins import TimestampMixin


class MeasurementType:
    """TODO (client confirmation required): whether 'No of Changeover' and
    'No of Coil Changeover' represent duration in minutes or number of occurrences.
    Current version treats both as duration in minutes. Switching a reason to
    count-based later should only require updating measurement_type.
    """

    DURATION_MINUTES = "duration_minutes"
    COUNT = "count"


class StoppageReason(TimestampMixin, Base):
    __tablename__ = "stoppage_reasons"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(160), unique=True, nullable=False)
    requires_details: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    details_label: Mapped[str | None] = mapped_column(String(120), nullable=True)
    measurement_type: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        default=MeasurementType.DURATION_MINUTES,
    )
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
