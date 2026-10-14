"""add salary extraction fields

Revision ID: 134a477efa87
Revises: 
Create Date: 2026-10-13 10:47:51.546804

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '134a477efa87'
down_revision = "0001_baseline"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('salary_posts', sa.Column('salary_min', sa.Float(), nullable=True))
    op.add_column('salary_posts', sa.Column('salary_max', sa.Float(), nullable=True))
    op.add_column('salary_posts', sa.Column('pay_basis', sa.String(length=20), server_default='unknown', nullable=False))
    op.add_column('salary_posts', sa.Column('has_equity', sa.Boolean(), nullable=True))
    op.add_column('salary_posts', sa.Column('bonus_included', sa.Boolean(), nullable=True))
    op.add_column('salary_posts', sa.Column('confidence', sa.Float(), nullable=True))
    op.add_column('salary_posts', sa.Column('evidence', sa.Text(), nullable=True))
    op.add_column('salary_posts', sa.Column('review_status', sa.String(length=20), server_default='approved', nullable=False))


def downgrade() -> None:
    op.drop_column('salary_posts', 'review_status')
    op.drop_column('salary_posts', 'evidence')
    op.drop_column('salary_posts', 'confidence')
    op.drop_column('salary_posts', 'bonus_included')
    op.drop_column('salary_posts', 'has_equity')
    op.drop_column('salary_posts', 'pay_basis')
    op.drop_column('salary_posts', 'salary_max')
    op.drop_column('salary_posts', 'salary_min')