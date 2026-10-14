"""hnsw index on embedding and honest source label

Revision ID: b2d4f6a8c013
Revises: a1c7e3d5b902
"""
from typing import Sequence, Union

from alembic import op

revision: str = "b2d4f6a8c013"
down_revision = "a1c7e3d5b902"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_salary_posts_embedding_hnsw "
        "ON salary_posts USING hnsw (embedding vector_cosine_ops)"
    )
    op.execute(
        "UPDATE salary_posts SET source = 'manual_paste' WHERE source = 'facebook'"
    )


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS ix_salary_posts_embedding_hnsw")
