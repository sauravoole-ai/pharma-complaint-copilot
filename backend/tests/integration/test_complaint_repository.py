from datetime import UTC, datetime

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.db_models import Base
from app.domain.schemas import (
    ComplaintFields,
    CompletenessResult,
    DraftAnalysisResult,
    DraftStatus,
    RiskSuggestion,
    Severity,
    SourceType,
)
from app.repositories.complaints import ComplaintRepository, DraftNotReadyError


@pytest.fixture
def repository():
    engine = create_engine("sqlite+pysqlite:///:memory:")
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        yield ComplaintRepository(session)


def analysis_result(*, complete: bool = True) -> DraftAnalysisResult:
    fields = ComplaintFields(
        complaint_source="Email",
        customer_name="Northstar Pharmacy",
        product_name="Amoxicillin Capsules",
        batch_lot_number="BMX240602" if complete else None,
        complaint_category="Product quality",
        complaint_description="Capsules appeared discolored on receipt.",
        affected_quantity="48 capsules",
    )
    return DraftAnalysisResult(
        source_type=SourceType.TEXT,
        fields=fields,
        completeness=CompletenessResult(
            is_complete=complete,
            missing_fields=[] if complete else ["batch_lot_number"],
        ),
        risk=RiskSuggestion(
            severity=Severity.MAJOR,
            next_action="Quarantine the reported batch and begin an investigation.",
            rationale="A possible product-quality defect may affect patient use.",
        ),
        summary="Customer reported discoloration in an amoxicillin capsule batch.",
        status=(DraftStatus.READY_TO_COMMIT if complete else DraftStatus.NEEDS_REVIEW),
    )


def test_draft_round_trip_and_update(repository):
    saved = repository.create_draft(analysis_result(), source_text_hash="a" * 64)

    loaded = repository.get_draft(saved.id)
    assert loaded == saved

    changed = analysis_result()
    changed.fields.affected_quantity = "50 capsules"
    updated = repository.update_draft(saved.id, changed)
    assert updated.fields.affected_quantity == "50 capsules"
    assert updated.updated_at >= saved.updated_at


def test_commit_is_idempotent(repository):
    saved = repository.create_draft(analysis_result(), source_text_hash="b" * 64)

    first = repository.commit_draft(saved.id, "demo-token-1")
    second = repository.commit_draft(saved.id, "demo-token-1")

    assert second.id == first.id
    assert first.source_draft_id == saved.id
    assert len(repository.list_complaints()) == 1


def test_incomplete_draft_cannot_be_committed(repository):
    saved = repository.create_draft(analysis_result(complete=False), source_text_hash="c" * 64)

    with pytest.raises(DraftNotReadyError):
        repository.commit_draft(saved.id, "demo-token-2")


def test_repository_timestamps_are_timezone_aware(repository):
    before = datetime.now(UTC)
    saved = repository.create_draft(analysis_result(), source_text_hash="d" * 64)
    after = datetime.now(UTC)

    assert before <= saved.created_at <= after
    assert saved.created_at.tzinfo is not None
