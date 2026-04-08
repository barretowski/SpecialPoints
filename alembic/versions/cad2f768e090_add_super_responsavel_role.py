"""add super_responsavel role

Revision ID: cad2f768e090
Revises: 7d5057901367
Create Date: 2026-04-08 09:48:16.811906

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'cad2f768e090'
down_revision: Union[str, None] = '7d5057901367'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("ALTER TYPE papelusuario ADD VALUE IF NOT EXISTS 'super_responsavel'")


def downgrade() -> None:
    pass
