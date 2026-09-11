from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db_models import ComplaintDraftModel, ComplaintModel
from app.domain.schemas import (
    ComplaintFields,
    ComplaintResponse,
    CompletenessResult,
    CopilotMessage,
    DraftAnalysisResult,
    DraftResponse,
    DraftStatus,
    RiskSuggestion,
    SourceType,
)


class DraftNotFoundError(LookupError):
    pass


class DraftNotReadyError(ValueError):
    pass


class DraftAlreadyCommittedError(ValueError):
    pass


def _aware(value: datetime) -> datetime:
    return value.replace(tzinfo=UTC) if value.tzinfo is None else value


def _draft_response(model: ComplaintDraftModel) -> DraftResponse:
    return DraftResponse(
        id=model.id,
        source_type=SourceType(model.source_type),
        fields=ComplaintFields.model_validate(model.structured_fields),
        completeness=CompletenessResult.model_validate(model.completeness),
        risk=RiskSuggestion.model_validate(model.risk_suggestion),
        summary=model.summary,
        status=DraftStatus(model.status),
        messages=[CopilotMessage.model_validate(message) for message in model.messages],
        created_at=_aware(model.created_at),
        updated_at=_aware(model.updated_at),
    )


def _complaint_response(model: ComplaintModel) -> ComplaintResponse:
    fields = {name: getattr(model, name) for name in ComplaintFields.model_fields}
    return ComplaintResponse(
        id=model.id,
        source_draft_id=model.source_draft_id,
        fields=ComplaintFields.model_validate(fields),
        risk=RiskSuggestion(
            severity=model.severity,
            next_action=model.next_action,
            rationale=model.risk_rationale,
        ),
        summary=model.summary,
        created_at=_aware(model.created_at),
    )


class ComplaintRepository:
    def __init__(self, session: Session):
        self.session = session

    def create_draft(
        self, analysis: DraftAnalysisResult, *, source_text_hash: str
    ) -> DraftResponse:
        draft = ComplaintDraftModel(
            source_type=analysis.source_type.value,
            source_text_hash=source_text_hash,
            structured_fields=analysis.fields.model_dump(mode="json"),
            completeness=analysis.completeness.model_dump(mode="json"),
            risk_suggestion=analysis.risk.model_dump(mode="json"),
            summary=analysis.summary,
            status=analysis.status.value,
            messages=[message.model_dump(mode="json") for message in analysis.messages],
        )
        self.session.add(draft)
        self.session.commit()
        self.session.refresh(draft)
        return _draft_response(draft)

    def get_draft(self, draft_id: UUID) -> DraftResponse | None:
        draft = self.session.get(ComplaintDraftModel, draft_id)
        return _draft_response(draft) if draft else None

    def update_draft(self, draft_id: UUID, analysis: DraftAnalysisResult) -> DraftResponse:
        draft = self._require_draft(draft_id)
        draft.source_type = analysis.source_type.value
        draft.structured_fields = analysis.fields.model_dump(mode="json")
        draft.completeness = analysis.completeness.model_dump(mode="json")
        draft.risk_suggestion = analysis.risk.model_dump(mode="json")
        draft.summary = analysis.summary
        draft.status = analysis.status.value
        draft.messages = [message.model_dump(mode="json") for message in analysis.messages]
        draft.updated_at = datetime.now(UTC)
        self.session.commit()
        self.session.refresh(draft)
        return _draft_response(draft)

    def commit_draft(self, draft_id: UUID, commit_token: str) -> ComplaintResponse:
        existing = self.session.scalar(
            select(ComplaintModel).where(ComplaintModel.commit_token == commit_token)
        )
        if existing:
            return _complaint_response(existing)

        committed_draft = self.session.scalar(
            select(ComplaintModel).where(ComplaintModel.source_draft_id == draft_id)
        )
        if committed_draft:
            raise DraftAlreadyCommittedError(
                "Draft was already committed with a different commit token"
            )

        draft = self._require_draft(draft_id)
        if draft.status != DraftStatus.READY_TO_COMMIT.value:
            raise DraftNotReadyError("Draft must be ready_to_commit before it can be committed")

        fields = ComplaintFields.model_validate(draft.structured_fields)
        risk = RiskSuggestion.model_validate(draft.risk_suggestion)
        complaint = ComplaintModel(
            source_draft_id=draft.id,
            commit_token=commit_token,
            **fields.model_dump(),
            severity=risk.severity.value,
            next_action=risk.next_action,
            risk_rationale=risk.rationale,
            summary=draft.summary,
            reviewer_confirmed=True,
        )
        draft.status = DraftStatus.COMMITTED.value
        draft.updated_at = datetime.now(UTC)
        self.session.add(complaint)
        self.session.commit()
        self.session.refresh(complaint)
        return _complaint_response(complaint)

    def list_complaints(self) -> list[ComplaintResponse]:
        complaints = self.session.scalars(
            select(ComplaintModel).order_by(ComplaintModel.created_at.desc())
        ).all()
        return [_complaint_response(complaint) for complaint in complaints]

    def _require_draft(self, draft_id: UUID) -> ComplaintDraftModel:
        draft = self.session.get(ComplaintDraftModel, draft_id)
        if not draft:
            raise DraftNotFoundError(f"Draft {draft_id} was not found")
        return draft
