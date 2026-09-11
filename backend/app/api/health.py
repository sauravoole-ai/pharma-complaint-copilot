from collections.abc import Callable

from fastapi import APIRouter
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.domain.schemas import StrictModel

APP_VERSION = "0.1.0"


class HealthResponse(StrictModel):
    status: str
    database: str
    version: str


def create_health_router(*, session_factory: Callable[[], Session]) -> APIRouter:
    router = APIRouter(prefix="/api/v1/health", tags=["health"])

    @router.get("", response_model=HealthResponse)
    def health() -> HealthResponse | JSONResponse:
        try:
            with session_factory() as session:
                session.execute(text("SELECT 1"))
            return HealthResponse(status="ok", database="available", version=APP_VERSION)
        except SQLAlchemyError:
            return JSONResponse(
                status_code=503,
                content={
                    "status": "degraded",
                    "database": "unavailable",
                    "version": APP_VERSION,
                },
            )

    return router
