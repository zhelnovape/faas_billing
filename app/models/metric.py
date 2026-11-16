from datetime import datetime

from sqlalchemy import BigInteger, Boolean, DateTime, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base, BigIntPK


class Metric(Base):
    __tablename__ = "metric"

    id: Mapped[int] = mapped_column(BigIntPK, primary_key=True)
    event_id: Mapped[str] = mapped_column(String(128), unique=True)
    function_id: Mapped[int] = mapped_column(ForeignKey("faas_function.id"))
    occurred_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    received_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    duration_ms: Mapped[int] = mapped_column(BigInteger)
    memory_mb: Mapped[int] = mapped_column(BigInteger)
    is_cold_start: Mapped[bool] = mapped_column(Boolean, default=False)
    calls_count: Mapped[int] = mapped_column(BigInteger, default=1)
