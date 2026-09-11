from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import sessionmaker

from app.config import Settings
from app.main import create_app
from tests.fakes import FakeLLMAdapter


def test_health_reports_only_safe_application_and_database_state():
    engine = create_engine("sqlite+pysqlite:///:memory:")
    app = create_app(
        settings=Settings(database_url="sqlite+pysqlite:///:memory:"),
        llm_adapter=FakeLLMAdapter(),
        session_factory=sessionmaker(bind=engine),
    )

    with TestClient(app) as client:
        response = client.get("/api/v1/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "database": "available",
        "version": "0.1.0",
    }


def test_health_failure_does_not_expose_database_error():
    def unavailable_session():
        raise OperationalError("SELECT secret", {}, RuntimeError("private database detail"))

    app = create_app(
        settings=Settings(database_url="sqlite+pysqlite:///:memory:"),
        llm_adapter=FakeLLMAdapter(),
        session_factory=unavailable_session,
    )

    with TestClient(app) as client:
        response = client.get("/api/v1/health")

    assert response.status_code == 503
    assert response.json() == {
        "status": "degraded",
        "database": "unavailable",
        "version": "0.1.0",
    }
    assert "private database detail" not in response.text
