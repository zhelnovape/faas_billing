from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class MetricCreate(BaseModel):
    event_id: str = Field(min_length=1, max_length=128)
    function_id: int
    occurred_at: datetime
    duration_ms: int = Field(ge=0)
    memory_mb: int = Field(gt=0)
    is_cold_start: bool = False
    calls_count: int = Field(default=1, ge=1)


class MetricRead(MetricCreate):
    model_config = ConfigDict(from_attributes=True)

    id: int
    received_at: datetime
