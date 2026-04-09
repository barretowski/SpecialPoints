"""add disponivel_em to tarefas

Revision ID: c7a2e3f8d1b4
Revises: b9e4f1a2c3d5
Create Date: 2026-04-08

"""
from alembic import op
import sqlalchemy as sa

revision = 'c7a2e3f8d1b4'
down_revision = 'b9e4f1a2c3d5'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('tarefas', sa.Column('disponivel_em', sa.DateTime(timezone=True), nullable=True))


def downgrade() -> None:
    op.drop_column('tarefas', 'disponivel_em')
