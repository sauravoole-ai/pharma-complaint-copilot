import os
from pathlib import Path

import pytest

from app.ai.graph import run_analysis
from app.ai.llm import GroqLLMAdapter
from app.config import Settings
from app.domain.schemas import Severity, SourceType
from app.services.validation import REQUIRED_FIELDS

pytestmark = pytest.mark.skipif(
    os.getenv("RUN_LIVE_AI") != "1",
    reason="Set RUN_LIVE_AI=1 to opt into the metered Groq smoke test",
)


def test_live_groq_returns_a_schema_valid_reviewable_analysis():
    settings = Settings()
    if not settings.groq_api_key:
        pytest.skip("GROQ_API_KEY is not configured")
    sample_path = Path(__file__).resolve().parents[3] / "samples" / "discoloration-complaint.txt"
    result = run_analysis(
        sample_path.read_text(),
        SourceType.TEXT,
        GroqLLMAdapter(api_key=settings.groq_api_key, model=settings.groq_model),
    )

    for field_name in REQUIRED_FIELDS:
        value = getattr(result.fields, field_name)
        assert value is not None and value.strip()
    assert result.risk.severity in set(Severity)
    assert result.risk.next_action.strip()
    assert result.risk.rationale.strip()
    assert any("Review" in message.content for message in result.messages)
