"""Bulk import infrastructure

Revision ID: 002
Revises: 001
Create Date: 2025-11-09 12:00:00

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    import_job_status = sa.Enum('PENDING', 'RUNNING', 'COMPLETED', 'FAILED', 'CANCELLED', name='importjobstatus')
    import_job_status.create(op.get_bind())

    op.create_table(
        'audio_import_jobs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('status', import_job_status, nullable=False, server_default='PENDING'),
        sa.Column('source', sa.String(), nullable=True),
        sa.Column('manifest_path', sa.String(), nullable=True),
        sa.Column('total_files', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('processed_files', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('duplicate_files', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('failed_files', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('error_log', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('started_at', sa.DateTime(), nullable=True),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_audio_import_jobs_id'), 'audio_import_jobs', ['id'], unique=False)
    op.create_index(op.f('ix_audio_import_jobs_user_id'), 'audio_import_jobs', ['user_id'], unique=False)
    op.create_index(op.f('ix_audio_import_jobs_status'), 'audio_import_jobs', ['status'], unique=False)

    op.add_column('audio_files', sa.Column('fingerprint', sa.String(), nullable=True))
    op.add_column('audio_files', sa.Column('import_job_id', sa.Integer(), nullable=True))
    op.create_index(op.f('ix_audio_files_fingerprint'), 'audio_files', ['fingerprint'], unique=False)
    op.create_index(op.f('ix_audio_files_import_job_id'), 'audio_files', ['import_job_id'], unique=False)
    op.create_unique_constraint('uq_audio_user_fingerprint', 'audio_files', ['user_id', 'fingerprint'])
    op.create_foreign_key(
        'fk_audio_files_import_job_id_audio_import_jobs',
        'audio_files',
        'audio_import_jobs',
        ['import_job_id'],
        ['id'],
        ondelete='SET NULL'
    )


def downgrade() -> None:
    op.drop_constraint('fk_audio_files_import_job_id_audio_import_jobs', 'audio_files', type_='foreignkey')
    op.drop_constraint('uq_audio_user_fingerprint', 'audio_files', type_='unique')
    op.drop_index(op.f('ix_audio_files_import_job_id'), table_name='audio_files')
    op.drop_index(op.f('ix_audio_files_fingerprint'), table_name='audio_files')
    op.drop_column('audio_files', 'import_job_id')
    op.drop_column('audio_files', 'fingerprint')

    op.drop_index(op.f('ix_audio_import_jobs_status'), table_name='audio_import_jobs')
    op.drop_index(op.f('ix_audio_import_jobs_user_id'), table_name='audio_import_jobs')
    op.drop_index(op.f('ix_audio_import_jobs_id'), table_name='audio_import_jobs')
    op.drop_table('audio_import_jobs')

    import_job_status = sa.Enum('PENDING', 'RUNNING', 'COMPLETED', 'FAILED', 'CANCELLED', name='importjobstatus')
    import_job_status.drop(op.get_bind())
