from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base, BigIntPK


class FaasFunction(Base):
    __tablename__ = "faas_function"

    id: Mapped[int] = mapped_column(BigIntPK, primary_key=True)
    client_id: Mapped[int] = mapped_column(ForeignKey("client.id"))
    tariff_id: Mapped[int] = mapped_column(ForeignKey("tariff.id"))
    name: Mapped[str] = mapped_column(String(255))
