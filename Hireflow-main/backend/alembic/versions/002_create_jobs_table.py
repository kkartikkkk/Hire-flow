"""create jobs table

Revision ID: 002
Revises: 001
Create Date: 2026-07-01
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import UUID

# revision identifiers, used by Alembic.
revision: str = "002"
down_revision: Union[str, None] = "001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "jobs",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "recruiter_id",
            UUID(as_uuid=True),
            sa.ForeignKey("recruiters.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("description", sa.Text, nullable=False),
        sa.Column("required_skills", sa.Text, nullable=False),
        sa.Column("experience_required", sa.Integer, nullable=False, server_default="0"),
        sa.Column("location", sa.String(255), nullable=False),
        sa.Column("employment_type", sa.String(50), nullable=False),
        sa.Column("salary_range", sa.String(255), nullable=True),
        sa.Column(
            "status",
            sa.Enum("OPEN", "CLOSED", name="job_status"),
            nullable=False,
            server_default="OPEN",
        ),
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

    # Indexes for filtering and lookups
    op.create_index("ix_jobs_recruiter_id", "jobs", ["recruiter_id"])
    op.create_index("ix_jobs_status", "jobs", ["status"])
    op.create_index("ix_jobs_title", "jobs", ["title"])
    op.create_index("ix_jobs_location", "jobs", ["location"])


def downgrade() -> None:
    op.drop_index("ix_jobs_location", table_name="jobs")
    op.drop_index("ix_jobs_title", table_name="jobs")
    op.drop_index("ix_jobs_status", table_name="jobs")
    op.drop_index("ix_jobs_recruiter_id", table_name="jobs")
    op.drop_table("jobs")

    # Drop the enum type
    sa.Enum(name="job_status").drop(op.get_bind(), checkfirst=True)
