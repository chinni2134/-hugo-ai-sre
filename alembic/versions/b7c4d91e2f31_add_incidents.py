"""add incidents

Revision ID: b7c4d91e2f31
Revises: aab3e782522e
Create Date: 2026-10-01
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "b7c4d91e2f31"
down_revision: Union[str, Sequence[str], None] = "aab3e782522e"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create incidents table."""

    op.create_table(
        "incidents",
        sa.Column(
            "id",
            sa.Integer(),
            autoincrement=True,
            nullable=False,
        ),
        sa.Column(
            "entity_id",
            sa.String(length=150),
            nullable=False,
        ),
        sa.Column(
            "severity",
            sa.String(length=30),
            nullable=False,
        ),
        sa.Column(
            "title",
            sa.String(length=255),
            nullable=False,
        ),
        sa.Column(
            "description",
            sa.Text(),
            nullable=False,
        ),
        sa.Column(
            "status",
            sa.String(length=30),
            nullable=False,
            server_default="open",
        ),
        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=True,
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index(
        "ix_incidents_entity_id",
        "incidents",
        ["entity_id"],
        unique=False,
    )

    op.create_index(
        "ix_incidents_created_at",
        "incidents",
        ["created_at"],
        unique=False,
    )


def downgrade() -> None:
    """Drop incidents table."""

    op.drop_index(
        "ix_incidents_created_at",
        table_name="incidents",
    )

    op.drop_index(
        "ix_incidents_entity_id",
        table_name="incidents",
    )

    op.drop_table("incidents")
