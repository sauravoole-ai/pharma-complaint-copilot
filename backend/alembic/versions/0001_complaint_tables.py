"""Create complaint draft and ledger tables.

Revision ID: 0001
Revises:
"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

FIELD_COLUMNS = (
    "complaint_source",
    "customer_name",
    "product_type",
    "product_name",
    "product_strength",
    "batch_lot_number",
    "affected_quantity",
    "manufacturing_date",
    "expiry_date",
    "originating_site_block",
    "impacted_non_product_materials",
    "complaint_category",
)


def upgrade() -> None:
    op.create_table(
        "complaint_drafts",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("source_type", sa.String(length=16), nullable=False),
        sa.Column("source_text_hash", sa.String(length=64), nullable=False),
        sa.Column("structured_fields", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("completeness", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("risk_suggestion", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("summary", sa.Text(), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("messages", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    columns = [sa.Column(name, sa.String(length=500), nullable=True) for name in FIELD_COLUMNS]
    op.create_table(
        "complaints",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("source_draft_id", sa.Uuid(), nullable=False),
        sa.Column("commit_token", sa.String(length=128), nullable=False),
        *columns,
        sa.Column("complaint_description", sa.Text(), nullable=True),
        sa.Column("customer_requested_action", sa.Text(), nullable=True),
        sa.Column("severity", sa.String(length=16), nullable=False),
        sa.Column("next_action", sa.Text(), nullable=False),
        sa.Column("risk_rationale", sa.Text(), nullable=False),
        sa.Column("summary", sa.Text(), nullable=False),
        sa.Column("reviewer_confirmed", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["source_draft_id"], ["complaint_drafts.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("commit_token"),
        sa.UniqueConstraint("source_draft_id"),
    )


def downgrade() -> None:
    op.drop_table("complaints")
    op.drop_table("complaint_drafts")
