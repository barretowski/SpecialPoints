"""add aprovacao_automatica to tarefas

Revision ID: d2e5f9a1b8c3
Revises: c7a2e3f8d1b4
Create Date: 2026-04-09

"""
from alembic import op
import sqlalchemy as sa

revision = 'd2e5f9a1b8c3'
down_revision = 'c7a2e3f8d1b4'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('tarefas', sa.Column(
        'aprovacao_automatica',
        sa.Boolean(),
        nullable=False,
        server_default='false',
    ))


def downgrade() -> None:
    op.drop_column('tarefas', 'aprovacao_automatica')
