"""initial tables

Revision ID: 0001
Revises:
Create Date: 2026-11-16 16:17:59.777525
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "client",
        sa.Column("id", sa.BigInteger().with_variant(sa.Integer(), "sqlite"), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "tariff",
        sa.Column("id", sa.BigInteger().with_variant(sa.Integer(), "sqlite"), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "faas_function",
        sa.Column("id", sa.BigInteger().with_variant(sa.Integer(), "sqlite"), nullable=False),
        sa.Column(
            "client_id", sa.BigInteger().with_variant(sa.Integer(), "sqlite"), nullable=False
        ),
        sa.Column(
            "tariff_id", sa.BigInteger().with_variant(sa.Integer(), "sqlite"), nullable=False
        ),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.ForeignKeyConstraint(
            ["client_id"],
            ["client.id"],
        ),
        sa.ForeignKeyConstraint(
            ["tariff_id"],
            ["tariff.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "tariff_version",
        sa.Column("id", sa.BigInteger().with_variant(sa.Integer(), "sqlite"), nullable=False),
        sa.Column(
            "tariff_id", sa.BigInteger().with_variant(sa.Integer(), "sqlite"), nullable=False
        ),
        sa.Column("version_number", sa.Integer(), nullable=False),
        sa.Column("valid_from", sa.DateTime(timezone=True), nullable=False),
        sa.Column("valid_to", sa.DateTime(timezone=True), nullable=True),
        sa.Column("price_per_call", sa.Numeric(precision=18, scale=9), nullable=False),
        sa.Column("price_per_ms", sa.Numeric(precision=18, scale=9), nullable=False),
        sa.Column("price_per_gb_second", sa.Numeric(precision=18, scale=9), nullable=False),
        sa.Column("cold_start_surcharge", sa.Numeric(precision=18, scale=9), nullable=False),
        sa.ForeignKeyConstraint(
            ["tariff_id"],
            ["tariff.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "metric",
        sa.Column("id", sa.BigInteger().with_variant(sa.Integer(), "sqlite"), nullable=False),
        sa.Column("event_id", sa.String(length=128), nullable=False),
        sa.Column(
            "function_id", sa.BigInteger().with_variant(sa.Integer(), "sqlite"), nullable=False
        ),
        sa.Column("occurred_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column(
            "received_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column("duration_ms", sa.BigInteger(), nullable=False),
        sa.Column("memory_mb", sa.BigInteger(), nullable=False),
        sa.Column("is_cold_start", sa.Boolean(), nullable=False),
        sa.Column("calls_count", sa.BigInteger(), nullable=False),
        sa.ForeignKeyConstraint(
            ["function_id"],
            ["faas_function.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("event_id"),
    )


def downgrade() -> None:
    op.drop_table("metric")
    op.drop_table("tariff_version")
    op.drop_table("faas_function")
    op.drop_table("tariff")
    op.drop_table("client")
