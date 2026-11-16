from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base, BigIntPK


class Tariff(Base):
    __tablename__ = "tariff"

    id: Mapped[int] = mapped_column(BigIntPK, primary_key=True)
    name: Mapped[str] = mapped_column(String(255))


class TariffVersion(Base):
    __tablename__ = "tariff_version"

    id: Mapped[int] = mapped_column(BigIntPK, primary_key=True)
    tariff_id: Mapped[int] = mapped_column(ForeignKey("tariff.id"))
    version_number: Mapped[int] = mapped_column(Integer, default=1)
    valid_from: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    valid_to: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    price_per_call: Mapped[Decimal] = mapped_column(Numeric(18, 9), default=0)
    price_per_ms: Mapped[Decimal] = mapped_column(Numeric(18, 9), default=0)
    price_per_gb_second: Mapped[Decimal] = mapped_column(Numeric(18, 9), default=0)
    cold_start_surcharge: Mapped[Decimal] = mapped_column(Numeric(18, 9), default=0)
