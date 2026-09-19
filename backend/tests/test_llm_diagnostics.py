import logging
from types import SimpleNamespace

import pytest

from app.ai.llm import GroqLLMAdapter, LLMProviderError
from app.domain.schemas import ComplaintFields


@pytest.mark.parametrize("status_code", [401, 429, 400])
def test_provider_failure_logs_status_without_secrets(caplog, status_code):
    class ProviderFailure(Exception):
        pass

    error = ProviderFailure("secret-key private-complaint raw-provider-body")
    error.status_code = status_code

    def create(**kwargs):
        raise error

    adapter = GroqLLMAdapter(api_key="secret-key", model="test-model")
    adapter._client = SimpleNamespace(
        chat=SimpleNamespace(completions=SimpleNamespace(create=create))
    )
    with caplog.at_level(logging.WARNING), pytest.raises(LLMProviderError):
        adapter.extract("private-complaint")

    assert f"status={status_code}" in caplog.text
    assert "schema=ComplaintFields" in caplog.text
    for sensitive in ("secret-key", "private-complaint", "raw-provider-body"):
        assert sensitive not in caplog.text


def test_invalid_model_json_logs_category_without_raw_output(caplog):
    def create(**kwargs):
        return SimpleNamespace(
            choices=[SimpleNamespace(message=SimpleNamespace(content="private-output"))]
        )

    adapter = GroqLLMAdapter(api_key="secret-key", model="test-model")
    adapter._client = SimpleNamespace(
        chat=SimpleNamespace(completions=SimpleNamespace(create=create))
    )
    with caplog.at_level(logging.WARNING), pytest.raises(LLMProviderError):
        adapter.extract("private-complaint")

    assert "category=invalid_structured_output" in caplog.text
    assert "schema=ComplaintFields" in caplog.text
    assert "private-output" not in caplog.text
    assert "private-complaint" not in caplog.text
    assert "secret-key" not in caplog.text


def test_summary_request_declares_structured_fields_authoritative_on_conflict():
    request = {}

    def create(**kwargs):
        request.update(kwargs)
        return SimpleNamespace(
            choices=[SimpleNamespace(message=SimpleNamespace(content='{"summary":"ok"}'))]
        )

    adapter = GroqLLMAdapter(api_key="test-key", model="test-model")
    adapter._client = SimpleNamespace(
        chat=SimpleNamespace(completions=SimpleNamespace(create=create))
    )
    fields = ComplaintFields(
        affected_quantity="25 packs",
        complaint_description="The customer originally reported 20 packs.",
    )

    adapter.summarize(fields)

    system_message = request["messages"][0]["content"]
    assert "structured fields are authoritative" in system_message.lower()
    assert "conflicting values from narrative fields" in system_message.lower()


def test_risk_request_keeps_recall_and_regulatory_decisions_human_controlled():
    request = {}

    def create(**kwargs):
        request.update(kwargs)
        return SimpleNamespace(
            choices=[
                SimpleNamespace(
                    message=SimpleNamespace(
                        content=(
                            '{"severity":"Major","next_action":"Escalate to QA",'
                            '"rationale":"Review required"}'
                        )
                    )
                )
            ]
        )

    adapter = GroqLLMAdapter(api_key="test-key", model="test-model")
    adapter._client = SimpleNamespace(
        chat=SimpleNamespace(completions=SimpleNamespace(create=create))
    )

    adapter.suggest_risk(ComplaintFields(complaint_category="Foreign matter"))

    system_message = request["messages"][0]["content"].lower()
    assert "do not direct a recall" in system_message
    assert "do not direct regulatory notification" in system_message
    assert "human quality reviewer" in system_message


def test_unsafe_risk_action_is_replaced_with_human_review_escalation():
    def create(**kwargs):
        return SimpleNamespace(
            choices=[
                SimpleNamespace(
                    message=SimpleNamespace(
                        content=(
                            '{"severity":"Critical",'
                            '"next_action":"Initiate a recall and notify the regulator",'
                            '"rationale":"Visible particulate requires urgent review"}'
                        )
                    )
                )
            ]
        )

    adapter = GroqLLMAdapter(api_key="test-key", model="test-model")
    adapter._client = SimpleNamespace(
        chat=SimpleNamespace(completions=SimpleNamespace(create=create))
    )

    risk = adapter.suggest_risk(ComplaintFields(complaint_category="Foreign matter"))

    assert risk.severity.value == "Critical"
    assert "qualified human quality reviewer" in risk.next_action
    assert "recall" not in risk.next_action.lower()
    assert "notify" not in risk.next_action.lower()
    assert risk.rationale == "Visible particulate requires urgent review"
