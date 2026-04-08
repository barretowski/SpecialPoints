"""add recorrencia e conquistas

Revision ID: b9e4f1a2c3d5
Revises: 1a3c0d25f174
Create Date: 2026-04-08

"""
from alembic import op
import sqlalchemy as sa

revision = 'b9e4f1a2c3d5'
down_revision = '1a3c0d25f174'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Recorrência nas tarefas
    op.add_column('tarefas', sa.Column('recorrencia', sa.String(20), nullable=True))

    # Tabela de conquistas
    op.create_table(
        'conquistas',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('usuario_id', sa.Integer(), nullable=False),
        sa.Column('tipo', sa.String(50), nullable=False),
        sa.Column('titulo', sa.String(100), nullable=False),
        sa.Column('descricao', sa.String(200), nullable=False),
        sa.Column('icone', sa.String(10), nullable=False),
        sa.Column(
            'conquistado_em',
            sa.DateTime(timezone=True),
            server_default=sa.text('now()'),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(['usuario_id'], ['usuarios.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_conquistas_id', 'conquistas', ['id'])
    op.create_index('ix_conquistas_usuario_id', 'conquistas', ['usuario_id'])


def downgrade() -> None:
    op.drop_index('ix_conquistas_usuario_id', 'conquistas')
    op.drop_index('ix_conquistas_id', 'conquistas')
    op.drop_table('conquistas')
    op.drop_column('tarefas', 'recorrencia')
