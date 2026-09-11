from datetime import datetime
from enum import StrEnum
from typing import Annotated
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, StringConstraints

ShortText = Annotated[str, StringConstraints(strip_whitespace=True, max_length=500)]
LongText = Annotated[str, StringConstraints(strip_whitespace=True, max_length=4000)]


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class DraftStatus(StrEnum):
    IDLE = "idle"
    PROCESSING = "processing"
    NEEDS_REVIEW = "needs_review"
    READY_TO_COMMIT = "ready_to_commit"
    COMMITTING = "committing"
    COMMITTED = "committed"
    FAILED = "failed"


class SourceType(StrEnum):
    TEXT = "text"
    PDF = "pdf"


class Severity(StrEnum):
    MINOR = "Minor"
    MAJOR = "Major"
    CRITICAL = "Critical"


class MessageRole(StrEnum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class ComplaintFields(StrictModel):
    complaint_source: ShortText | None = None
    customer_name: ShortText | None = None
    product_type: ShortText | None = None
    product_name: ShortText | None = None
    product_strength: ShortText | None = None
    batch_lot_number: ShortText | None = None
    affected_quantity: ShortText | None = None
    manufacturing_date: ShortText | None = None
    expiry_date: ShortText | None = None
    originating_site_block: ShortText | None = None
    impacted_non_product_materials: ShortText | None = None
    complaint_category: ShortText | None = None
    complaint_description: LongText | None = None
    customer_requested_action: LongText | None = None


class RiskSuggestion(StrictModel):
    severity: Severity
    next_action: LongText
    rationale: LongText


class CompletenessResult(StrictModel):
    is_complete: bool
    missing_fields: list[str] = Field(default_factory=list)
    uncertain_fields: list[str] = Field(default_factory=list)


class CopilotMessage(StrictModel):
    role: MessageRole
    content: LongText


class DraftAnalysisResult(StrictModel):
    source_type: SourceType
    fields: ComplaintFields
    completeness: CompletenessResult
    risk: RiskSuggestion
    summary: LongText
    status: DraftStatus
    messages: list[CopilotMessage] = Field(default_factory=list)


class DraftResponse(DraftAnalysisResult):
    id: UUID
    created_at: datetime
    updated_at: datetime


class ComplaintResponse(StrictModel):
    id: UUID
    source_draft_id: UUID
    fields: ComplaintFields
    risk: RiskSuggestion
    summary: LongText
    created_at: datetime
