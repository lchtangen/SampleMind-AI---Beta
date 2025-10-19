"""Initial schema

Revision ID: 001
Revises: 
Create Date: 2025-10-19 22:00:00

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create users table
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('email', sa.String(), nullable=False),
        sa.Column('hashed_password', sa.String(), nullable=False),
        sa.Column('full_name', sa.String(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('is_superuser', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('is_premium', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('is_beta_user', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('last_login_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)

    # Create audio_files table
    op.create_table(
        'audio_files',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('filename', sa.String(), nullable=False),
        sa.Column('original_filename', sa.String(), nullable=False),
        sa.Column('file_path', sa.String(), nullable=False),
        sa.Column('file_format', sa.String(), nullable=False),
        sa.Column('file_size', sa.Integer(), nullable=False),
        sa.Column('duration', sa.Float(), nullable=True),
        sa.Column('sample_rate', sa.Integer(), nullable=True),
        sa.Column('channels', sa.Integer(), nullable=True),
        sa.Column('bit_depth', sa.Integer(), nullable=True),
        sa.Column('status', sa.Enum('UPLOADED', 'PROCESSING', 'COMPLETED', 'FAILED', name='audiostatus'), nullable=False),
        sa.Column('error_message', sa.String(), nullable=True),
        sa.Column('uploaded_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('processed_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_audio_files_id'), 'audio_files', ['id'], unique=False)
    op.create_index(op.f('ix_audio_files_user_id'), 'audio_files', ['user_id'], unique=False)
    op.create_index(op.f('ix_audio_files_status'), 'audio_files', ['status'], unique=False)
    op.create_index(op.f('ix_audio_files_uploaded_at'), 'audio_files', ['uploaded_at'], unique=False)

    # Create audio_analysis table
    op.create_table(
        'audio_analysis',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('audio_id', sa.Integer(), nullable=False),
        sa.Column('tempo', sa.Float(), nullable=True),
        sa.Column('key', sa.String(), nullable=True),
        sa.Column('time_signature', sa.String(), nullable=True),
        sa.Column('loudness', sa.Float(), nullable=True),
        sa.Column('energy', sa.Float(), nullable=True),
        sa.Column('danceability', sa.Float(), nullable=True),
        sa.Column('valence', sa.Float(), nullable=True),
        sa.Column('acousticness', sa.Float(), nullable=True),
        sa.Column('instrumentalness', sa.Float(), nullable=True),
        sa.Column('liveness', sa.Float(), nullable=True),
        sa.Column('speechiness', sa.Float(), nullable=True),
        sa.Column('spectral_centroid', sa.Float(), nullable=True),
        sa.Column('spectral_rolloff', sa.Float(), nullable=True),
        sa.Column('zero_crossing_rate', sa.Float(), nullable=True),
        sa.Column('genres', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('moods', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('instruments', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('tags', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('description', sa.String(), nullable=True),
        sa.Column('similarity_score', sa.Float(), nullable=True),
        sa.Column('analyzed_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['audio_id'], ['audio_files.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_audio_analysis_id'), 'audio_analysis', ['id'], unique=False)
    op.create_index(op.f('ix_audio_analysis_audio_id'), 'audio_analysis', ['audio_id'], unique=True)


def downgrade() -> None:
    op.drop_index(op.f('ix_audio_analysis_audio_id'), table_name='audio_analysis')
    op.drop_index(op.f('ix_audio_analysis_id'), table_name='audio_analysis')
    op.drop_table('audio_analysis')
    
    op.drop_index(op.f('ix_audio_files_uploaded_at'), table_name='audio_files')
    op.drop_index(op.f('ix_audio_files_status'), table_name='audio_files')
    op.drop_index(op.f('ix_audio_files_user_id'), table_name='audio_files')
    op.drop_index(op.f('ix_audio_files_id'), table_name='audio_files')
    op.drop_table('audio_files')
    
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_index(op.f('ix_users_id'), table_name='users')
    op.drop_table('users')
    
    sa.Enum('UPLOADED', 'PROCESSING', 'COMPLETED', 'FAILED', name='audiostatus').drop(op.get_bind())
