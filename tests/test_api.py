def make_event(function_id, event_id="event-1", **fields):
    event = {
        "event_id": event_id,
        "function_id": function_id,
        "occurred_at": "2026-11-01T10:00:00Z",
        "duration_ms": 1000,
        "memory_mb": 1024,
    }
    event.update(fields)
    return event


def test_create_metric(client, function_id):
    response = client.post("/api/v1/metrics", json=make_event(function_id))

    assert response.status_code == 201
    assert response.json()["calls_count"] == 1
    assert len(client.get("/api/v1/metrics").json()) == 1


def test_duplicate_metric_rejected(client, function_id):
    client.post("/api/v1/metrics", json=make_event(function_id))
    response = client.post("/api/v1/metrics", json=make_event(function_id))

    assert response.status_code == 409
    assert len(client.get("/api/v1/metrics").json()) == 1


def test_invalid_metric_rejected(client, function_id):
    response = client.post("/api/v1/metrics", json=make_event(function_id, duration_ms=-1))

    assert response.status_code == 422


def test_metric_for_unknown_function(client):
    response = client.post("/api/v1/metrics", json=make_event(999))

    assert response.status_code == 404


def test_metrics_stats(client, function_id):
    client.post("/api/v1/metrics", json=make_event(function_id, "e1", is_cold_start=True))
    client.post("/api/v1/metrics", json=make_event(function_id, "e2", calls_count=2))

    stats = client.get("/api/v1/metrics/stats").json()[0]

    assert stats["events_count"] == 2
    assert stats["calls_count"] == 3
    assert stats["total_duration_ms"] == 2000
    assert stats["cold_starts"] == 1


def test_function_cost_for_period(client, function_id):
    client.post("/api/v1/metrics", json=make_event(function_id, "e1", is_cold_start=True))
    client.post(
        "/api/v1/metrics",
        json=make_event(function_id, "e2", occurred_at="2026-11-05T10:00:00Z"),
    )

    response = client.get(
        f"/api/v1/billing/functions/{function_id}/cost",
        params={"date_from": "2026-11-01T00:00:00Z", "date_to": "2026-11-02T00:00:00Z"},
    )

    assert response.status_code == 200
    assert response.json()["calls_count"] == 1
    assert response.json()["total_cost"] == "1.062000"
