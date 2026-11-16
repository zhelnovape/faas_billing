from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models import FaasFunction, Metric
from app.schemas.metric import MetricCreate, MetricRead
from app.schemas.stats import FunctionStats
from app.services.metrics import get_stats

router = APIRouter(prefix="/metrics", tags=["metrics"])


@router.post("", response_model=MetricRead, status_code=201)
def create_metric(data: MetricCreate, db: Session = Depends(get_db)):
    if db.get(FaasFunction, data.function_id) is None:
        raise HTTPException(404, "Function not found")
    if db.scalar(select(Metric).where(Metric.event_id == data.event_id)) is not None:
        raise HTTPException(409, "Event already exists")

    metric = Metric(**data.model_dump())
    db.add(metric)
    db.commit()
    db.refresh(metric)
    return metric


@router.get("", response_model=list[MetricRead])
def list_metrics(function_id: int | None = None, db: Session = Depends(get_db)):
    query = select(Metric).order_by(Metric.occurred_at.desc())
    if function_id is not None:
        query = query.where(Metric.function_id == function_id)
    return db.scalars(query).all()


@router.get("/stats", response_model=list[FunctionStats])
def metrics_stats(
    function_id: int | None = None,
    client_id: int | None = None,
    date_from: datetime | None = None,
    date_to: datetime | None = None,
    db: Session = Depends(get_db),
):
    return get_stats(db, function_id, client_id, date_from, date_to)
