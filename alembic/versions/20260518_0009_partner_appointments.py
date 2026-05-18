"""add partner appointments

Revision ID: 20260518_0009
Revises: 20260514_0008
Create Date: 2026-05-18 00:09:00.000000
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa

revision = "20260518_0009"
down_revision = "20260514_0008"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "partner_appointments",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("client_id", sa.Integer(), sa.ForeignKey("client_profiles.id"), nullable=False),
        sa.Column("partner_id", sa.Integer(), sa.ForeignKey("partners.id"), nullable=False),
        sa.Column("offer_id", sa.Integer(), sa.ForeignKey("partner_offers.id"), nullable=True),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="new"),
        sa.Column("client_name", sa.String(length=255), nullable=True),
        sa.Column("client_phone", sa.String(length=64), nullable=False),
        sa.Column("client_email", sa.String(length=255), nullable=True),
        sa.Column("comment", sa.Text(), nullable=True),
        sa.Column("desired_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("source", sa.String(length=64), nullable=True, server_default="web"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("confirmed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("cancelled_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("rejected_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_partner_appointments_client_id", "partner_appointments", ["client_id"])
    op.create_index("ix_partner_appointments_partner_id", "partner_appointments", ["partner_id"])
    op.create_index("ix_partner_appointments_offer_id", "partner_appointments", ["offer_id"])
    op.create_index("ix_partner_appointments_status", "partner_appointments", ["status"])
    op.create_index(
        "ix_partner_appointments_partner_status_created",
        "partner_appointments",
        ["partner_id", "status", "created_at"],
    )
    op.create_index(
        "ix_partner_appointments_client_created",
        "partner_appointments",
        ["client_id", "created_at"],
    )


def downgrade() -> None:
    op.drop_index("ix_partner_appointments_client_created", table_name="partner_appointments")
    op.drop_index("ix_partner_appointments_partner_status_created", table_name="partner_appointments")
    op.drop_index("ix_partner_appointments_status", table_name="partner_appointments")
    op.drop_index("ix_partner_appointments_offer_id", table_name="partner_appointments")
    op.drop_index("ix_partner_appointments_partner_id", table_name="partner_appointments")
    op.drop_index("ix_partner_appointments_client_id", table_name="partner_appointments")
    op.drop_table("partner_appointments")
