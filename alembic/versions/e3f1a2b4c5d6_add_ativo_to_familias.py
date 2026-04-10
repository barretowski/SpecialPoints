"""add ativo to familias

Revision ID: e3f1a2b4c5d6
Revises: d2e5f9a1b8c3
Create Date: 2026-04-10 15:24:10.535636

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'e3f1a2b4c5d6'
down_revision: Union[str, None] = 'd2e5f9a1b8c3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('familias', sa.Column(
        'ativo',
        sa.Boolean(),
        nullable=False,
        server_default='true',
    ))


def downgrade() -> None:
    op.drop_column('familias', 'ativo')
