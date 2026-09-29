"""Добавляет поле с фотографией позиции каталога.

Revision ID: 9f2c1a4b7d10
Revises: 33f3b72b2055
"""
from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "9f2c1a4b7d10"
down_revision = "33f3b72b2055"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "solutions",
        sa.Column("photo_file", sa.String(length=160), nullable=True),
    )
    op.create_index("ix_solutions_photo_file", "solutions", ["photo_file"])


def downgrade() -> None:
    op.drop_index("ix_solutions_photo_file", table_name="solutions")
    op.drop_column("solutions", "photo_file")
