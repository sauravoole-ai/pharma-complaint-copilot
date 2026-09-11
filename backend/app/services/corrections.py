from pydantic import ValidationError

from app.ai.llm import LLMAdapter
from app.domain.schemas import (
    ComplaintFields,
    CompletenessResult,
    CopilotMessage,
    DraftStatus,
    MessageRole,
    StrictModel,
)
from app.services.validation import validate_and_classify

EDITABLE_FIELD_NAMES = frozenset(ComplaintFields.model_fields)
FIELD_LABELS = {"batch_lot_number": "batch / lot number"}


class InvalidCorrection(ValueError):
    pass


class CorrectionResult(StrictModel):
    fields: ComplaintFields
    completeness: CompletenessResult
    status: DraftStatus
    changed_fields: list[str]
    assistant_message: CopilotMessage


def apply_correction(
    current_fields: ComplaintFields,
    message: str,
    llm: LLMAdapter,
) -> CorrectionResult:
    instruction = message.strip()
    if not instruction:
        raise InvalidCorrection("Correction message cannot be blank")

    patch = llm.correction_patch(current_fields, instruction)
    if not patch:
        raise InvalidCorrection("The correction did not identify any field changes")
    if set(patch) - EDITABLE_FIELD_NAMES:
        raise InvalidCorrection("The correction attempted to change unsupported fields")

    try:
        updated_fields = ComplaintFields.model_validate({**current_fields.model_dump(), **patch})
    except ValidationError as exc:
        raise InvalidCorrection("One or more corrected values are invalid") from exc

    changed_fields = [
        name for name in patch if getattr(updated_fields, name) != getattr(current_fields, name)
    ]
    if not changed_fields:
        raise InvalidCorrection("The correction did not change any field values")

    completeness, status = validate_and_classify(updated_fields)
    labels = [FIELD_LABELS.get(name, name.replace("_", " ")) for name in changed_fields]
    assistant_message = CopilotMessage(
        role=MessageRole.ASSISTANT,
        content=f"Updated: {', '.join(labels)}.",
    )
    return CorrectionResult(
        fields=updated_fields,
        completeness=completeness,
        status=status,
        changed_fields=changed_fields,
        assistant_message=assistant_message,
    )
