"""add system entities

Revision ID: aed90552cebc
Revises: 42ca745ef028
Create Date: 2026-10-01 10:38:56.290622

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "aed90552cebc"
down_revision: Union[str, Sequence[str], None] = "42ca745ef028"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "system_entities",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("entity_id", sa.String(length=100), nullable=False),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("entity_type", sa.String(length=100), nullable=False),
        sa.Column(
            "environment",
            sa.String(length=100),
            nullable=True,
            server_default="development",
        ),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("entity_id"),
    )

    op.create_index(
        "ix_system_entities_entity_id",
        "system_entities",
        ["entity_id"],
        unique=True,
    )


def downgrade() -> None:
    op.drop_index(
        "ix_system_entities_entity_id",
        table_name="system_entities",
    )
    op.drop_table("system_entities")
