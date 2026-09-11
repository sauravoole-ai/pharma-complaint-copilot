from datetime import UTC, datetime
from typing import Any
from uuid import UUID, uuid4

from sqlalchemy import JSON, Boolean, DateTime, ForeignKey, String, Text, Uuid
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

JSON_DOCUMENT = JSON().with_variant(JSONB(), "postgresql")


def utc_now() -> datetime:
    return datetime.now(UTC)


class Base(DeclarativeBase):
    pass


class ComplaintDraftModel(Base):
    __tablename__ = "complaint_drafts"

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    source_type: Mapped[str] = mapped_column(String(16), nullable=False)
    source_text_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    structured_fields: Mapped[dict[str, Any]] = mapped_column(JSON_DOCUMENT, nullable=False)
    completeness: Mapped[dict[str, Any]] = mapped_column(JSON_DOCUMENT, nullable=False)
    risk_suggestion: Mapped[dict[str, Any]] = mapped_column(JSON_DOCUMENT, nullable=False)
    summary: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    messages: Mapped[list[dict[str, Any]]] = mapped_column(
        JSON_DOCUMENT, nullable=False, default=list
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=utc_now
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=utc_now, onupdate=utc_now
    )


class ComplaintModel(Base):
    __tablename__ = "complaints"

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    source_draft_id: Mapped[UUID] = mapped_column(
        ForeignKey("complaint_drafts.id", ondelete="RESTRICT"), nullable=False, unique=True
    )
    commit_token: Mapped[str] = mapped_column(String(128), nullable=False, unique=True)

    complaint_source: Mapped[str | None] = mapped_column(String(500))
    customer_name: Mapped[str | None] = mapped_column(String(500))
    product_type: Mapped[str | None] = mapped_column(String(500))
    product_name: Mapped[str | None] = mapped_column(String(500))
    product_strength: Mapped[str | None] = mapped_column(String(500))
    batch_lot_number: Mapped[str | None] = mapped_column(String(500))
    affected_quantity: Mapped[str | None] = mapped_column(String(500))
    manufacturing_date: Mapped[str | None] = mapped_column(String(500))
    expiry_date: Mapped[str | None] = mapped_column(String(500))
    originating_site_block: Mapped[str | None] = mapped_column(String(500))
    impacted_non_product_materials: Mapped[str | None] = mapped_column(String(500))
    complaint_category: Mapped[str | None] = mapped_column(String(500))
    complaint_description: Mapped[str | None] = mapped_column(Text)
    customer_requested_action: Mapped[str | None] = mapped_column(Text)

    severity: Mapped[str] = mapped_column(String(16), nullable=False)
    next_action: Mapped[str] = mapped_column(Text, nullable=False)
    risk_rationale: Mapped[str] = mapped_column(Text, nullable=False)
    summary: Mapped[str] = mapped_column(Text, nullable=False)
    reviewer_confirmed: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=utc_now
    )
