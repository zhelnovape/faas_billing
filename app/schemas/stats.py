from decimal import Decimal

from pydantic import BaseModel


class FunctionStats(BaseModel):
    function_id: int
    events_count: int
    calls_count: int
    total_duration_ms: int
    avg_duration_ms: float
    avg_memory_mb: float
    max_memory_mb: int
    gb_seconds: Decimal
    cold_starts: int
