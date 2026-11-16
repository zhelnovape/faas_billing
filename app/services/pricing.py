from decimal import ROUND_HALF_UP, Decimal

from app.models import Metric, TariffVersion

MIN_DURATION_MS = 100
MIN_MEMORY_MB = 128
PRECISION = Decimal("0.000001")


def billable_duration(duration_ms: int) -> int:
    return max(duration_ms, MIN_DURATION_MS)


def billable_memory(memory_mb: int) -> int:
    return max(memory_mb, MIN_MEMORY_MB)


def gb_seconds(memory_mb: int, duration_ms: int) -> Decimal:
    return Decimal(memory_mb) / 1024 * Decimal(duration_ms) / 1000


def round_money(value: Decimal) -> Decimal:
    return value.quantize(PRECISION, rounding=ROUND_HALF_UP)


def calculate_cost(metrics: list[Metric], tariff: TariffVersion) -> dict:
    calls = 0
    duration = 0
    resources = Decimal(0)
    cold_starts = 0

    for metric in metrics:
        metric_duration = billable_duration(metric.duration_ms)
        calls += metric.calls_count
        duration += metric_duration
        resources += gb_seconds(billable_memory(metric.memory_mb), metric_duration)
        if metric.is_cold_start:
            cold_starts += 1

    calls_cost = round_money(calls * tariff.price_per_call)
    time_cost = round_money(duration * tariff.price_per_ms)
    resource_cost = round_money(resources * tariff.price_per_gb_second)
    cold_start_cost = round_money(cold_starts * tariff.cold_start_surcharge)

    return {
        "calls_count": calls,
        "billable_duration_ms": duration,
        "gb_seconds": resources,
        "cold_starts": cold_starts,
        "calls_cost": calls_cost,
        "time_cost": time_cost,
        "resource_cost": resource_cost,
        "cold_start_cost": cold_start_cost,
        "total_cost": calls_cost + time_cost + resource_cost + cold_start_cost,
    }
