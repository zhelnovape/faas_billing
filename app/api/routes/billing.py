from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models import FaasFunction, Metric, TariffVersion
from app.schemas.billing import CostRead
from app.services.pricing import calculate_cost

router = APIRouter(prefix="/billing", tags=["billing"])


@router.get("/functions/{function_id}/cost", response_model=CostRead)
def function_cost(
    function_id: int,
    date_from: datetime | None = None,
    date_to: datetime | None = None,
    db: Session = Depends(get_db),
):
    function = db.get(FaasFunction, function_id)
    if function is None:
        raise HTTPException(404, "Function not found")

    tariff = db.scalar(
        select(TariffVersion)
        .where(TariffVersion.tariff_id == function.tariff_id)
        .order_by(TariffVersion.version_number.desc())
    )
    if tariff is None:
        raise HTTPException(404, "Tariff not found")

    query = select(Metric).where(Metric.function_id == function_id)
    if date_from is not None:
        query = query.where(Metric.occurred_at >= date_from)
    if date_to is not None:
        query = query.where(Metric.occurred_at < date_to)
    metrics = db.scalars(query).all()

    return CostRead(
        function_id=function_id,
        tariff_id=function.tariff_id,
        **calculate_cost(metrics, tariff),
    )
