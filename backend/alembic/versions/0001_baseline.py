"""baseline schema

Revision ID: 0001_baseline
Revises:
"""
from typing import Sequence, Union

import pgvector.sqlalchemy
import sqlalchemy as sa
from alembic import op

revision: str = "0001_baseline"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")
    op.create_table(
        "salary_posts",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("raw_text", sa.Text(), nullable=False),
        sa.Column("role", sa.String(length=100), nullable=True),
        sa.Column("years_experience", sa.Float(), nullable=True),
        sa.Column("salary", sa.Float(), nullable=True),
        sa.Column("company_stage", sa.String(length=50), nullable=True),
        sa.Column("location", sa.String(length=100), nullable=True),
        sa.Column("embedding", pgvector.sqlalchemy.Vector(1536), nullable=True),
        sa.Column("source", sa.String(length=100), nullable=True),
        sa.Column("post_date", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "query_logs",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("query", sa.Text(), nullable=False),
        sa.Column("latency_retrieval", sa.Float(), nullable=True),
        sa.Column("latency_reranking", sa.Float(), nullable=True),
        sa.Column("latency_generation", sa.Float(), nullable=True),
        sa.Column("latency_total", sa.Float(), nullable=True),
        sa.Column("posts_retrieved", sa.Integer(), nullable=True),
        sa.Column("posts_after_rerank", sa.Integer(), nullable=True),
        sa.Column("retrieved_post_ids", sa.JSON(), nullable=True),
        sa.Column("tokens_used", sa.Integer(), nullable=True),
        sa.Column("estimated_cost_usd", sa.Float(), nullable=True),
        sa.Column("success", sa.Boolean(), nullable=False),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("query_logs")
    op.drop_table("salary_posts")