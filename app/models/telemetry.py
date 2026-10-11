from datetime import datetime

from sqlalchemy import DateTime, Float, String

from sqlalchemy.orm import Mapped, mapped_column

from app.database.postgres import Base


class TelemetryRecord(Base):

    __tablename__ = "telemetry_records"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
    )

    entity_id: Mapped[str] = mapped_column(
        String(150),
        index=True,
        nullable=False,
    )

    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    cpu_percent: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    memory_percent: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    collected_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        index=True,
    )
