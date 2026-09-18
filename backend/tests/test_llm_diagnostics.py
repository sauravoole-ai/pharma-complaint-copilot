import logging
from types import SimpleNamespace

import pytest

from app.ai.llm import GroqLLMAdapter, LLMProviderError


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
