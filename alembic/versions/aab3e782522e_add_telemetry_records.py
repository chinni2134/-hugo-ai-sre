"""add telemetry records

Revision ID: aab3e782522e
Revises: aed90552cebc
Create Date: 2026-10-01 10:48:04.108723

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "aab3e782522e"
down_revision: Union[str, Sequence[str], None] = "aed90552cebc"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create telemetry_records table."""

    op.create_table(
        "telemetry_records",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("entity_id", sa.String(length=150), nullable=False),
        sa.Column("status", sa.String(length=50), nullable=False),
        sa.Column("cpu_percent", sa.Float(), nullable=False),
        sa.Column("memory_percent", sa.Float(), nullable=False),
        sa.Column("collected_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index(
        "ix_telemetry_records_entity_id",
        "telemetry_records",
        ["entity_id"],
        unique=False,
    )

    op.create_index(
        "ix_telemetry_records_collected_at",
        "telemetry_records",
        ["collected_at"],
        unique=False,
    )


def downgrade() -> None:
    """Drop telemetry_records table."""

    op.drop_index(
        "ix_telemetry_records_collected_at",
        table_name="telemetry_records",
    )

    op.drop_index(
        "ix_telemetry_records_entity_id",
        table_name="telemetry_records",
    )

    op.drop_table("telemetry_records")
