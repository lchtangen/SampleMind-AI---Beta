"""add audio embeddings table

Revision ID: 003_add_audio_embeddings
Revises: 002_bulk_import_infrastructure
Create Date: 2025-11-09 00:00:00
"""

from alembic import op
import sqlalchemy as sa

try:  # pragma: no cover - optional dependency
    from pgvector.sqlalchemy import Vector  # type: ignore
except Exception:  # pragma: no cover
    Vector = None

# revision identifiers, used by Alembic.
revision = '003_add_audio_embeddings'
down_revision = '002_bulk_import_infrastructure'
branch_labels = None
depends_on = None


def _embedding_column():
    if Vector is not None:
        return Vector(512)
    return sa.JSON()


def upgrade() -> None:
    op.create_table(
        'audio_embeddings',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('audio_id', sa.Integer(), sa.ForeignKey('audio_files.id', ondelete='CASCADE'), nullable=False, unique=True),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('model', sa.String(length=255), nullable=False, server_default='laion/clap-htsat-unfused'),
        sa.Column('source', sa.String(length=128), nullable=True),
        sa.Column('embedding', _embedding_column(), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now(), nullable=False),
    )
    op.create_index('ix_audio_embeddings_user_id', 'audio_embeddings', ['user_id'])
    op.create_index('ix_audio_embeddings_model', 'audio_embeddings', ['model'])


def downgrade() -> None:
    op.drop_index('ix_audio_embeddings_model', table_name='audio_embeddings')
    op.drop_index('ix_audio_embeddings_user_id', table_name='audio_embeddings')
    op.drop_table('audio_embeddings')
