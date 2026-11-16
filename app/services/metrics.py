from datetime import datetime
from decimal import Decimal

from sqlalchemy import case, func, select
from sqlalchemy.orm import Session

from app.models import FaasFunction, Metric


def get_stats(
    db: Session,
    function_id: int | None = None,
    client_id: int | None = None,
    date_from: datetime | None = None,
    date_to: datetime | None = None,
) -> list[dict]:
    query = (
        select(
            Metric.function_id,
            func.count(Metric.id).label("events_count"),
            func.sum(Metric.calls_count).label("calls_count"),
            func.sum(Metric.duration_ms).label("total_duration_ms"),
            func.avg(Metric.duration_ms).label("avg_duration_ms"),
            func.avg(Metric.memory_mb).label("avg_memory_mb"),
            func.max(Metric.memory_mb).label("max_memory_mb"),
            func.sum(Metric.memory_mb * Metric.duration_ms).label("mb_ms"),
            func.sum(case((Metric.is_cold_start, 1), else_=0)).label("cold_starts"),
        )
        .join(FaasFunction, FaasFunction.id == Metric.function_id)
        .group_by(Metric.function_id)
        .order_by(Metric.function_id)
    )
    if function_id is not None:
        query = query.where(Metric.function_id == function_id)
    if client_id is not None:
        query = query.where(FaasFunction.client_id == client_id)
    if date_from is not None:
        query = query.where(Metric.occurred_at >= date_from)
    if date_to is not None:
        query = query.where(Metric.occurred_at < date_to)

    result = []
    for row in db.execute(query).mappings():
        item = dict(row)
        item["gb_seconds"] = Decimal(item.pop("mb_ms")) / 1024 / 1000
        result.append(item)
    return result
