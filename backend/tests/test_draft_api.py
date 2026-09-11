from io import BytesIO
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from pypdf import PdfWriter
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.config import Settings
from app.db_models import Base
from app.main import create_app
from tests.fakes import FakeLLMAdapter


@pytest.fixture
def client():
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    factory = sessionmaker(bind=engine, expire_on_commit=False)
    app = create_app(
        settings=Settings(database_url="sqlite+pysqlite:///:memory:"),
        llm_adapter=FakeLLMAdapter(),
        session_factory=factory,
    )
    with TestClient(app) as test_client:
        yield test_client


def image_only_pdf() -> bytes:
    output = BytesIO()
    writer = PdfWriter()
    writer.add_blank_page(width=200, height=200)
    writer.write(output)
    return output.getvalue()


def test_analyze_text_persists_and_returns_draft(client):
    response = client.post(
        "/api/v1/complaint-drafts/analyze-text",
        json={
            "text": (
                "Northstar Pharmacy reported 48 discolored Amoxicillin capsules "
                "from batch AMX240602 and requested an investigation."
            )
        },
    )

    assert response.status_code == 201
    assert response.json()["fields"]["batch_lot_number"] == "AMX240602"
    assert response.json()["source_type"] == "text"


def test_scanned_pdf_is_rejected(client):
    response = client.post(
        "/api/v1/complaint-drafts/analyze-file",
        files={"file": ("scan.pdf", image_only_pdf(), "application/pdf")},
    )

    assert response.status_code == 422
    assert response.json()["code"] == "insufficient_pdf_text"


def test_non_pdf_upload_is_rejected(client):
    response = client.post(
        "/api/v1/complaint-drafts/analyze-file",
        files={"file": ("complaint.txt", b"plain text", "text/plain")},
    )

    assert response.status_code == 415
    assert response.json()["code"] == "unsupported_media_type"


def test_conversation_correction_updates_and_revalidates_draft(client):
    created = client.post(
        "/api/v1/complaint-drafts/analyze-text",
        json={"text": "A sufficiently detailed complaint for the deterministic fake adapter."},
    ).json()

    response = client.patch(
        f"/api/v1/complaint-drafts/{created['id']}/conversation",
        json={"message": "The batch number is BMX240602."},
    )

    assert response.status_code == 200
    assert response.json()["fields"]["batch_lot_number"] == "BMX240602"
    assert response.json()["status"] == "ready_to_commit"
    assert response.json()["messages"][-1]["content"] == "Updated: batch / lot number."


def test_conversation_for_missing_draft_returns_404(client):
    response = client.patch(
        f"/api/v1/complaint-drafts/{uuid4()}/conversation",
        json={"message": "Correct the batch number."},
    )

    assert response.status_code == 404
    assert response.json()["code"] == "draft_not_found"
