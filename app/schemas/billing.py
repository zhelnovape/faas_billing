from decimal import Decimal

from pydantic import BaseModel


class CostRead(BaseModel):
    function_id: int
    tariff_id: int
    calls_count: int
    billable_duration_ms: int
    gb_seconds: Decimal
    cold_starts: int
    calls_cost: Decimal
    time_cost: Decimal
    resource_cost: Decimal
    cold_start_cost: Decimal
    total_cost: Decimal
