from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.config import Settings
from app.db_models import Base
from app.main import create_app
from tests.fakes import FakeLLMAdapter


def make_client(*, complete: bool = True) -> TestClient:
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    factory = sessionmaker(bind=engine, expire_on_commit=False)
    return TestClient(
        create_app(
            settings=Settings(database_url="sqlite+pysqlite:///:memory:"),
            llm_adapter=FakeLLMAdapter(omit_batch=not complete),
            session_factory=factory,
        )
    )


def create_draft(client: TestClient) -> dict:
    response = client.post(
        "/api/v1/complaint-drafts/analyze-text",
        json={"text": "A detailed customer complaint suitable for the deterministic fake."},
    )
    assert response.status_code == 201
    return response.json()


def test_incomplete_draft_cannot_be_committed():
    with make_client(complete=False) as client:
        draft = create_draft(client)
        response = client.post(
            "/api/v1/complaints",
            json={"draft_id": draft["id"], "commit_token": "token-a"},
        )

    assert response.status_code == 409
    assert response.json()["code"] == "draft_not_ready"


def test_repeated_commit_returns_same_record_and_one_ledger_row():
    with make_client() as client:
        draft = create_draft(client)
        payload = {"draft_id": draft["id"], "commit_token": "token-b"}

        first = client.post("/api/v1/complaints", json=payload)
        second = client.post("/api/v1/complaints", json=payload)
        ledger = client.get("/api/v1/complaints")

    assert first.status_code == 201
    assert second.status_code == 201
    assert first.json()["id"] == second.json()["id"]
    assert len(ledger.json()) == 1


def test_committed_draft_rejects_a_different_token():
    with make_client() as client:
        draft = create_draft(client)
        first = client.post(
            "/api/v1/complaints",
            json={"draft_id": draft["id"], "commit_token": "original-token"},
        )
        second = client.post(
            "/api/v1/complaints",
            json={"draft_id": draft["id"], "commit_token": "different-token"},
        )

    assert first.status_code == 201
    assert second.status_code == 409
    assert second.json()["code"] == "draft_already_committed"


def test_missing_draft_returns_404():
    with make_client() as client:
        response = client.post(
            "/api/v1/complaints",
            json={
                "draft_id": "00000000-0000-0000-0000-000000000001",
                "commit_token": "token-c",
            },
        )

    assert response.status_code == 404
    assert response.json()["code"] == "draft_not_found"
