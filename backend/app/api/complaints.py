from collections.abc import Callable
from uuid import UUID

from fastapi import APIRouter
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.domain.schemas import ComplaintResponse
from app.repositories.complaints import (
    ComplaintRepository,
    DraftAlreadyCommittedError,
    DraftNotFoundError,
    DraftNotReadyError,
)


class CommitComplaintRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    draft_id: UUID
    commit_token: str = Field(min_length=1, max_length=128)


def _error(status_code: int, code: str, message: str) -> JSONResponse:
    return JSONResponse(status_code=status_code, content={"code": code, "message": message})


def create_complaints_router(*, session_factory: Callable[[], Session]) -> APIRouter:
    router = APIRouter(prefix="/api/v1/complaints", tags=["complaints"])

    @router.post("", response_model=ComplaintResponse, status_code=201)
    def commit_complaint(
        payload: CommitComplaintRequest,
    ) -> ComplaintResponse | JSONResponse:
        try:
            with session_factory() as session:
                return ComplaintRepository(session).commit_draft(
                    payload.draft_id, payload.commit_token
                )
        except DraftNotFoundError:
            return _error(404, "draft_not_found", "Complaint draft was not found")
        except DraftNotReadyError:
            return _error(409, "draft_not_ready", "Review all required fields before committing")
        except DraftAlreadyCommittedError:
            return _error(
                409,
                "draft_already_committed",
                "This draft was already committed with a different token",
            )
        except SQLAlchemyError:
            return _error(503, "database_unavailable", "The complaint ledger is unavailable")

    @router.get("", response_model=list[ComplaintResponse])
    def list_complaints() -> list[ComplaintResponse] | JSONResponse:
        try:
            with session_factory() as session:
                return ComplaintRepository(session).list_complaints()
        except SQLAlchemyError:
            return _error(503, "database_unavailable", "The complaint ledger is unavailable")

    return router
