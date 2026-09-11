from collections.abc import Callable
from hashlib import sha256
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, File, UploadFile
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy.orm import Session

from app.ai.graph import AnalysisInputError, run_analysis
from app.ai.llm import LLMAdapter, LLMConfigurationError, LLMProviderError
from app.config import Settings
from app.domain.schemas import (
    CopilotMessage,
    DraftAnalysisResult,
    DraftResponse,
    MessageRole,
    SourceType,
)
from app.repositories.complaints import ComplaintRepository
from app.services.corrections import InvalidCorrection, apply_correction
from app.services.pdf_text import PdfTextError, extract_pdf_text

SessionFactory = Callable[[], Session]


class AnalyzeTextRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    text: str = Field(min_length=1, max_length=30_000)


class CorrectionRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    message: str = Field(min_length=1, max_length=2_000)


def _error(status_code: int, code: str, message: str) -> JSONResponse:
    return JSONResponse(status_code=status_code, content={"code": code, "message": message})


def create_drafts_router(
    *, settings: Settings, llm: LLMAdapter, session_factory: SessionFactory
) -> APIRouter:
    router = APIRouter(prefix="/api/v1/complaint-drafts", tags=["complaint drafts"])

    def analyze_and_save(text: str, source_type: SourceType) -> DraftResponse | JSONResponse:
        try:
            result = run_analysis(text, source_type, llm)
            digest = sha256(text.encode("utf-8")).hexdigest()
            with session_factory() as session:
                return ComplaintRepository(session).create_draft(result, source_text_hash=digest)
        except AnalysisInputError as exc:
            return _error(422, "invalid_source_text", str(exc))
        except LLMConfigurationError:
            return _error(503, "ai_not_configured", "AI analysis is not configured")
        except LLMProviderError:
            return _error(502, "ai_analysis_failed", "AI analysis could not be completed")

    @router.post("/analyze-text", response_model=DraftResponse, status_code=201)
    def analyze_text(payload: AnalyzeTextRequest) -> DraftResponse | JSONResponse:
        return analyze_and_save(payload.text, SourceType.TEXT)

    @router.post("/analyze-file", response_model=DraftResponse, status_code=201)
    async def analyze_file(file: Annotated[UploadFile, File()]) -> DraftResponse | JSONResponse:
        if file.content_type != "application/pdf":
            return _error(415, "unsupported_media_type", "Only PDF files are supported")
        content = await file.read(settings.max_upload_bytes + 1)
        try:
            text = extract_pdf_text(content, max_upload_bytes=settings.max_upload_bytes)
        except PdfTextError as exc:
            return _error(exc.status_code, exc.code, str(exc))
        return analyze_and_save(text, SourceType.PDF)

    @router.patch("/{draft_id}/conversation", response_model=DraftResponse)
    def correct_draft(draft_id: UUID, payload: CorrectionRequest) -> DraftResponse | JSONResponse:
        with session_factory() as session:
            repository = ComplaintRepository(session)
            draft = repository.get_draft(draft_id)
            if not draft:
                return _error(404, "draft_not_found", "Complaint draft was not found")
            try:
                correction = apply_correction(draft.fields, payload.message, llm)
                analysis = DraftAnalysisResult(
                    source_type=draft.source_type,
                    fields=correction.fields,
                    completeness=correction.completeness,
                    risk=llm.suggest_risk(correction.fields),
                    summary=llm.summarize(correction.fields),
                    status=correction.status,
                    messages=[
                        *draft.messages,
                        CopilotMessage(role=MessageRole.USER, content=payload.message),
                        correction.assistant_message,
                    ],
                )
                return repository.update_draft(draft_id, analysis)
            except InvalidCorrection as exc:
                return _error(422, "invalid_correction", str(exc))
            except LLMConfigurationError:
                return _error(503, "ai_not_configured", "AI analysis is not configured")
            except LLMProviderError:
                return _error(502, "ai_analysis_failed", "AI analysis could not be completed")

    return router
