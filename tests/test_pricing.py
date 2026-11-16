from decimal import Decimal

from app.models import Metric, TariffVersion
from app.services.pricing import calculate_cost

TARIFF = TariffVersion(
    price_per_call=Decimal("0.01"),
    price_per_ms=Decimal("0.001"),
    price_per_gb_second=Decimal("0.002"),
    cold_start_surcharge=Decimal("0.05"),
)


def make_metric(duration_ms, memory_mb, calls_count=1, is_cold_start=False):
    return Metric(
        duration_ms=duration_ms,
        memory_mb=memory_mb,
        calls_count=calls_count,
        is_cold_start=is_cold_start,
    )


def test_cost_breakdown():
    cost = calculate_cost([make_metric(1000, 1024, calls_count=3, is_cold_start=True)], TARIFF)

    assert cost["calls_cost"] == Decimal("0.030000")
    assert cost["time_cost"] == Decimal("1.000000")
    assert cost["resource_cost"] == Decimal("0.002000")
    assert cost["cold_start_cost"] == Decimal("0.050000")
    assert cost["total_cost"] == Decimal("1.082000")


def test_min_duration_and_memory():
    cost = calculate_cost([make_metric(50, 64)], TARIFF)

    assert cost["billable_duration_ms"] == 100
    assert cost["gb_seconds"] == Decimal("0.0125")


def test_small_costs_are_not_lost():
    tariff = TariffVersion(
        price_per_call=Decimal("0.0000002"),
        price_per_ms=Decimal(0),
        price_per_gb_second=Decimal(0),
        cold_start_surcharge=Decimal(0),
    )
    metrics = [make_metric(100, 128) for _ in range(10)]

    assert calculate_cost(metrics, tariff)["calls_cost"] == Decimal("0.000002")


def test_no_metrics_costs_nothing():
    assert calculate_cost([], TARIFF)["total_cost"] == 0
