import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.database import Base, get_db
from app.main import app


@pytest.fixture
def client():
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    Base.metadata.create_all(engine)
    TestSession = sessionmaker(bind=engine)

    def override_get_db():
        db = TestSession()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()
    engine.dispose()


@pytest.fixture
def function_id(client):
    client_id = client.post("/api/v1/clients", json={"name": "Test client"}).json()["id"]
    tariff_id = client.post(
        "/api/v1/tariffs",
        json={
            "name": "Test tariff",
            "price_per_call": "0.01",
            "price_per_ms": "0.001",
            "price_per_gb_second": "0.002",
            "cold_start_surcharge": "0.05",
        },
    ).json()["id"]
    response = client.post(
        "/api/v1/functions",
        json={"client_id": client_id, "tariff_id": tariff_id, "name": "test-function"},
    )
    return response.json()["id"]
