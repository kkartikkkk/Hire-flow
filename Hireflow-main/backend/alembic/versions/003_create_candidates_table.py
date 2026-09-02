"""create candidates table

Revision ID: 003
Revises: 002
Create Date: 2026-07-01
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import UUID

# revision identifiers, used by Alembic.
revision: str = "003"
down_revision: Union[str, None] = "002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "candidates",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "job_id",
            UUID(as_uuid=True),
            sa.ForeignKey("jobs.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("email", sa.String(255), nullable=False),
        sa.Column("phone", sa.String(50), nullable=False),
        sa.Column("resume_filename", sa.String(255), nullable=True),
        sa.Column("skills", sa.Text, nullable=False),
        sa.Column("experience", sa.Text, nullable=False),
        sa.Column("education", sa.Text, nullable=False),
        sa.Column("fit_score", sa.Integer, nullable=True),
        sa.Column("fit_reason", sa.Text, nullable=True),
        sa.Column(
            "status",
            sa.Enum("ACTIVE", "SHORTLISTED", "REJECTED", "HIRED", name="candidate_status"),
            nullable=False,
            server_default="ACTIVE",
        ),
        sa.Column("notes", sa.Text, nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )

    # Indexes: job_id, email, status, name
    op.create_index("ix_candidates_job_id", "candidates", ["job_id"])
    op.create_index("ix_candidates_email", "candidates", ["email"])
    op.create_index("ix_candidates_status", "candidates", ["status"])
    op.create_index("ix_candidates_name", "candidates", ["name"])


def downgrade() -> None:
    op.drop_index("ix_candidates_name", table_name="candidates")
    op.drop_index("ix_candidates_status", table_name="candidates")
    op.drop_index("ix_candidates_email", table_name="candidates")
    op.drop_index("ix_candidates_job_id", table_name="candidates")
    op.drop_table("candidates")

    # Drop the enum type
    sa.Enum(name="candidate_status").drop(op.get_bind(), checkfirst=True)
