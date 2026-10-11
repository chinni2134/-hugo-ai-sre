"""add embeddings to knowledge chunks

Revision ID: 42ca745ef028
Revises: 135f68dcbc9c
Create Date: 2026-09-29 22:43:38.194437
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from pgvector.sqlalchemy import Vector


revision: str = "42ca745ef028"
down_revision: Union[str, Sequence[str], None] = "135f68dcbc9c"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "knowledge_chunks",
        sa.Column(
            "embedding",
            Vector(384),
            nullable=True,
        ),
    )


def downgrade() -> None:
    op.drop_column(
        "knowledge_chunks",
        "embedding",
    )
