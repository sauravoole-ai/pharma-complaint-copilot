import pytest

from app.ai.graph import AnalysisInputError, run_analysis
from app.domain.schemas import DraftStatus, Severity, SourceType
from tests.fakes import FakeLLMAdapter

DISCOLORATION_TEXT = """
Northstar Pharmacy reported that 48 Amoxicillin 500 mg capsules from batch
AMX240602 appeared discolored. They requested replacement and an investigation.
"""


def test_graph_returns_reviewable_major_draft():
    llm = FakeLLMAdapter()

    result = run_analysis(DISCOLORATION_TEXT, SourceType.TEXT, llm)

    assert result.fields.batch_lot_number == "AMX240602"
    assert result.risk.severity == Severity.MAJOR
    assert result.status == DraftStatus.READY_TO_COMMIT
    assert result.completeness.is_complete is True
    assert llm.calls == ["extract", "suggest_risk", "summarize"]


def test_graph_marks_missing_required_field_for_review():
    result = run_analysis(DISCOLORATION_TEXT, SourceType.TEXT, FakeLLMAdapter(omit_batch=True))

    assert result.status == DraftStatus.NEEDS_REVIEW
    assert result.completeness.missing_fields == ["batch_lot_number"]


def test_graph_rejects_blank_source_before_calling_model():
    llm = FakeLLMAdapter()

    with pytest.raises(AnalysisInputError):
        run_analysis("  \n\t ", SourceType.TEXT, llm)

    assert llm.calls == []
