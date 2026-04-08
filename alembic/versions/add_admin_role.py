"""add admin role to papelusuario enum

Revision ID: add_admin_role
Revises: 276469b0b966
Create Date: 2026-04-08

"""
from typing import Sequence, Union

from alembic import op

revision: str = "add_admin_role"
down_revision: Union[str, None] = "276469b0b966"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # PostgreSQL: adiciona valor ao enum existente (irreversível nativamente)
    op.execute("ALTER TYPE papelusuario ADD VALUE IF NOT EXISTS 'admin'")


def downgrade() -> None:
    # Não é possível remover valores de enum no PostgreSQL sem recriar o tipo.
    # Para reverter, seria necessário migrar dados e recriar o enum.
    pass
