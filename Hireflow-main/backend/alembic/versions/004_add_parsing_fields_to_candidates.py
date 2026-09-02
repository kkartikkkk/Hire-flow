"""add parsing fields to candidates

Revision ID: 004
Revises: 003
Create Date: 2026-07-01
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "004"
down_revision: Union[str, None] = "003"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add columns parsed_resume and parsed_at
    op.add_column("candidates", sa.Column("parsed_resume", sa.Text(), nullable=True))
    op.add_column("candidates", sa.Column("parsed_at", sa.DateTime(timezone=True), nullable=True))


def downgrade() -> None:
    op.drop_column("candidates", "parsed_at")
    op.drop_column("candidates", "parsed_resume")
