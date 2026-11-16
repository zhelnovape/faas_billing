from datetime import UTC, datetime

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models import Tariff, TariffVersion
from app.schemas.tariff import TariffCreate, TariffRead

router = APIRouter(prefix="/tariffs", tags=["tariffs"])


def to_read(tariff: Tariff, version: TariffVersion) -> TariffRead:
    return TariffRead(
        id=tariff.id,
        name=tariff.name,
        price_per_call=version.price_per_call,
        price_per_ms=version.price_per_ms,
        price_per_gb_second=version.price_per_gb_second,
        cold_start_surcharge=version.cold_start_surcharge,
    )


@router.post("", response_model=TariffRead, status_code=201)
def create_tariff(data: TariffCreate, db: Session = Depends(get_db)):
    tariff = Tariff(name=data.name)
    db.add(tariff)
    db.flush()

    version = TariffVersion(
        tariff_id=tariff.id,
        version_number=1,
        valid_from=datetime.now(UTC),
        **data.model_dump(exclude={"name"}),
    )
    db.add(version)
    db.commit()
    return to_read(tariff, version)


@router.get("", response_model=list[TariffRead])
def list_tariffs(db: Session = Depends(get_db)):
    rows = db.execute(
        select(Tariff, TariffVersion)
        .join(TariffVersion, TariffVersion.tariff_id == Tariff.id)
        .order_by(Tariff.id)
    ).all()
    return [to_read(tariff, version) for tariff, version in rows]
