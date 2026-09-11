from collections.abc import Callable

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from app.ai.llm import GroqLLMAdapter, LLMAdapter
from app.api.drafts import create_drafts_router
from app.api.health import router as health_router
from app.config import Settings, get_settings
from app.db import SessionLocal


def create_app(
    *,
    settings: Settings | None = None,
    llm_adapter: LLMAdapter | None = None,
    session_factory: Callable[[], Session] | None = None,
) -> FastAPI:
    resolved_settings = settings or get_settings()
    resolved_llm = llm_adapter or GroqLLMAdapter(
        api_key=resolved_settings.groq_api_key,
        model=resolved_settings.groq_model,
    )
    resolved_session_factory = session_factory or SessionLocal

    application = FastAPI(
        title="Pharma Complaint Copilot API",
        version="0.1.0",
    )
    application.add_middleware(
        CORSMiddleware,
        allow_origins=[resolved_settings.frontend_origin],
        allow_credentials=True,
        allow_methods=["GET", "POST", "PATCH"],
        allow_headers=["Content-Type", "Idempotency-Key"],
    )
    application.include_router(health_router)
    application.include_router(
        create_drafts_router(
            settings=resolved_settings,
            llm=resolved_llm,
            session_factory=resolved_session_factory,
        )
    )
    return application


app = create_app()
