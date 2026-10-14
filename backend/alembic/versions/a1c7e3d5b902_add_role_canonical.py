"""add role_canonical

Revision ID: a1c7e3d5b902
Revises: 134a477efa87
Create Date: 2026-10-13 15:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

from app.tools.normalize_role import normalize_role

revision: str = "a1c7e3d5b902"
down_revision = "134a477efa87"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "salary_posts",
        sa.Column("role_canonical", sa.String(length=30), nullable=True),
    )
    op.create_index(
        "ix_salary_posts_role_canonical", "salary_posts", ["role_canonical"]
    )

    connection = op.get_bind()
    rows = connection.execute(sa.text("SELECT id, role FROM salary_posts")).all()
    for row in rows:
        connection.execute(
            sa.text("UPDATE salary_posts SET role_canonical = :canonical WHERE id = :id"),
            {"canonical": normalize_role(row.role or ""), "id": row.id},
        )


def downgrade() -> None:
    op.drop_index("ix_salary_posts_role_canonical", table_name="salary_posts")
    op.drop_column("salary_posts", "role_canonical")
