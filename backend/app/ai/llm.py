import json
import logging
from typing import Protocol, TypeVar

from groq import Groq
from pydantic import BaseModel, ValidationError, field_validator

from app.domain.schemas import ComplaintFields, RiskSuggestion, StrictModel

StructuredOutput = TypeVar("StructuredOutput", bound=BaseModel)
logger = logging.getLogger(__name__)


class LLMConfigurationError(RuntimeError):
    pass


class LLMProviderError(RuntimeError):
    """A safe internal error that intentionally excludes raw provider output."""


class LLMAdapter(Protocol):
    def extract(self, source_text: str) -> ComplaintFields: ...

    def suggest_risk(self, fields: ComplaintFields) -> RiskSuggestion: ...

    def summarize(self, fields: ComplaintFields) -> str: ...

    def correction_patch(
        self, fields: ComplaintFields, instruction: str
    ) -> dict[str, str | None]: ...


class SummaryOutput(StrictModel):
    summary: str


class CorrectionOutput(StrictModel):
    updates: dict[str, str | None]

    @field_validator("updates")
    @classmethod
    def only_complaint_fields(cls, updates: dict[str, str | None]) -> dict[str, str | None]:
        unknown = set(updates) - set(ComplaintFields.model_fields)
        if unknown:
            raise ValueError("Correction contains unsupported complaint fields")
        return updates


class GroqLLMAdapter:
    def __init__(self, *, api_key: str | None, model: str):
        self.api_key = api_key
        self.model = model
        self._client: Groq | None = None

    @property
    def client(self) -> Groq:
        if not self.api_key:
            raise LLMConfigurationError("GROQ_API_KEY is required")
        if self._client is None:
            self._client = Groq(api_key=self.api_key)
        return self._client

    def extract(self, source_text: str) -> ComplaintFields:
        return self._structured(
            system=(
                "You extract pharmaceutical customer complaint facts. Use only facts stated in "
                "the source. Return null for unknown values; never infer batch numbers, dates, "
                "quantities, customers, products, or requested actions."
            ),
            user=f"Extract the complaint into the required schema.\n\nSOURCE:\n{source_text}",
            schema=ComplaintFields,
        )

    def suggest_risk(self, fields: ComplaintFields) -> RiskSuggestion:
        suggestion = self._structured(
            system=(
                "You are a pharmaceutical complaint triage assistant. Suggest Minor, Major, or "
                "Critical severity, a prudent next action, and a concise rationale. This is a "
                "reviewable suggestion, not a final regulatory or clinical decision. Do not "
                "direct a recall and do not direct regulatory notification. Recommend escalation "
                "to a human quality reviewer for investigation and controlled decisions."
            ),
            user=f"Assess this extracted complaint:\n{fields.model_dump_json(indent=2)}",
            schema=RiskSuggestion,
        )
        action = suggestion.next_action.lower()
        if any(term in action for term in ("recall", "regulator", "regulatory author")):
            suggestion = suggestion.model_copy(
                update={
                    "next_action": (
                        "Escalate promptly to a qualified human quality reviewer for "
                        "investigation, containment assessment, and controlled field or "
                        "regulatory decisions under approved procedures."
                    )
                }
            )
        return suggestion

    def summarize(self, fields: ComplaintFields) -> str:
        result = self._structured(
            system=(
                "Summarize the supplied complaint facts in one or two neutral sentences. Do not "
                "add facts, causality, or conclusions. The structured fields are authoritative. "
                "When values conflict, use structured field values and do not repeat conflicting "
                "values from narrative fields such as complaint_source or complaint_description."
            ),
            user=fields.model_dump_json(indent=2),
            schema=SummaryOutput,
        )
        return result.summary

    def correction_patch(self, fields: ComplaintFields, instruction: str) -> dict[str, str | None]:
        result = self._structured(
            system=(
                "Translate the user's correction into a minimal field patch. Include only fields "
                "the user explicitly changed. Never modify other values."
            ),
            user=(
                f"CURRENT FIELDS:\n{fields.model_dump_json(indent=2)}\n\nCORRECTION:\n{instruction}"
            ),
            schema=CorrectionOutput,
        )
        return result.updates

    def _structured(
        self,
        *,
        system: str,
        user: str,
        schema: type[StructuredOutput],
    ) -> StructuredOutput:
        schema_json = json.dumps(schema.model_json_schema(), separators=(",", ":"))
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                temperature=0,
                max_completion_tokens=1_200,
                response_format={"type": "json_object"},
                messages=[
                    {
                        "role": "system",
                        "content": (
                            f"{system}\nReturn JSON matching this schema exactly: {schema_json}"
                        ),
                    },
                    {"role": "user", "content": user},
                ],
            )
            content = response.choices[0].message.content
            if not content:
                raise ValueError("Provider returned empty content")
            return schema.model_validate_json(content)
        except (IndexError, TypeError, ValueError, ValidationError) as exc:
            logger.warning(
                "Groq analysis failed category=invalid_structured_output schema=%s",
                schema.__name__,
            )
            raise LLMProviderError("The AI response did not match the required schema") from exc
        except Exception as exc:
            status = getattr(exc, "status_code", None)
            safe_status = status if type(status) is int and 100 <= status <= 599 else "unknown"
            logger.warning(
                "Groq analysis failed category=provider_request status=%s schema=%s",
                safe_status,
                schema.__name__,
            )
            raise LLMProviderError("The AI provider request failed") from exc
