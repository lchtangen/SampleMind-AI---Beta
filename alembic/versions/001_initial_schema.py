"""Initial database schema

Revision ID: 001
Revises: 
Create Date: 2025-10-19 18:30:00

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create initial database schema"""
    
    # Enable pgvector extension
    op.execute('CREATE EXTENSION IF NOT EXISTS vector')
    op.execute('CREATE EXTENSION IF NOT EXISTS pg_trgm')  # For full-text search
    op.execute('CREATE EXTENSION IF NOT EXISTS btree_gin')  # For GIN indexes
    
    # Users table
    op.create_table(
        'users',
        sa.Column('id', sa.String(100), primary_key=True),
        sa.Column('email', sa.String(255), nullable=False, unique=True),
        sa.Column('username', sa.String(100), nullable=False, unique=True),
        sa.Column('hashed_password', sa.String(255), nullable=False),
        sa.Column('role', sa.String(50), nullable=False, server_default='free'),
        sa.Column('is_active', sa.Boolean, nullable=False, server_default='true'),
        sa.Column('is_verified', sa.Boolean, nullable=False, server_default='false'),
        sa.Column('total_uploads', sa.Integer, nullable=False, server_default='0'),
        sa.Column('storage_used_mb', sa.Float, nullable=False, server_default='0'),
        sa.Column('api_calls_today', sa.Integer, nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('last_login', sa.DateTime(timezone=True)),
        sa.Column('metadata', postgresql.JSONB, server_default='{}'),
    )
    
    # Indexes for users
    op.create_index('idx_users_email', 'users', ['email'])
    op.create_index('idx_users_username', 'users', ['username'])
    op.create_index('idx_users_role', 'users', ['role'])
    op.create_index('idx_users_created_at', 'users', ['created_at'])
    
    # API Keys table
    op.create_table(
        'api_keys',
        sa.Column('key_id', sa.String(100), primary_key=True),
        sa.Column('user_id', sa.String(100), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('key_hash', sa.String(255), nullable=False, unique=True),
        sa.Column('prefix', sa.String(20), nullable=False),
        sa.Column('permissions', postgresql.JSONB, nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('expires_at', sa.DateTime(timezone=True)),
        sa.Column('last_used_at', sa.DateTime(timezone=True)),
        sa.Column('is_active', sa.Boolean, nullable=False, server_default='true'),
        sa.Column('usage_count', sa.Integer, nullable=False, server_default='0'),
        sa.Column('rate_limit_per_minute', sa.Integer, nullable=False, server_default='60'),
        sa.Column('ip_whitelist', postgresql.JSONB, server_default='[]'),
        sa.Column('description', sa.Text),
        sa.Column('environment', sa.String(50), nullable=False, server_default='production'),
    )
    
    # Indexes for API keys
    op.create_index('idx_api_keys_user_id', 'api_keys', ['user_id'])
    op.create_index('idx_api_keys_prefix', 'api_keys', ['prefix'])
    op.create_index('idx_api_keys_is_active', 'api_keys', ['is_active'])
    
    # OAuth Accounts table
    op.create_table(
        'oauth_accounts',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('user_id', sa.String(100), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('provider', sa.String(50), nullable=False),
        sa.Column('provider_user_id', sa.String(255), nullable=False),
        sa.Column('access_token', sa.Text),
        sa.Column('refresh_token', sa.Text),
        sa.Column('expires_at', sa.DateTime(timezone=True)),
        sa.Column('linked_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('metadata', postgresql.JSONB, server_default='{}'),
    )
    
    # Unique constraint on provider + provider_user_id
    op.create_unique_constraint('uq_oauth_provider_user', 'oauth_accounts', ['provider', 'provider_user_id'])
    op.create_index('idx_oauth_user_id', 'oauth_accounts', ['user_id'])
    
    # Audio Collections table
    op.create_table(
        'audio_collections',
        sa.Column('id', sa.String(100), primary_key=True),
        sa.Column('user_id', sa.String(100), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text),
        sa.Column('is_public', sa.Boolean, nullable=False, server_default='false'),
        sa.Column('file_count', sa.Integer, nullable=False, server_default='0'),
        sa.Column('total_duration', sa.Float, nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('tags', postgresql.JSONB, server_default='[]'),
        sa.Column('metadata', postgresql.JSONB, server_default='{}'),
    )
    
    # Indexes for collections
    op.create_index('idx_collections_user_id', 'audio_collections', ['user_id'])
    op.create_index('idx_collections_is_public', 'audio_collections', ['is_public'])
    op.create_index('idx_collections_created_at', 'audio_collections', ['created_at'])
    
    # Sessions table (for refresh tokens)
    op.create_table(
        'user_sessions',
        sa.Column('id', sa.String(100), primary_key=True),
        sa.Column('user_id', sa.String(100), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('refresh_token_hash', sa.String(255), nullable=False, unique=True),
        sa.Column('device_info', postgresql.JSONB, server_default='{}'),
        sa.Column('ip_address', sa.String(45)),
        sa.Column('user_agent', sa.Text),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('last_activity', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('is_active', sa.Boolean, nullable=False, server_default='true'),
    )
    
    # Indexes for sessions
    op.create_index('idx_sessions_user_id', 'user_sessions', ['user_id'])
    op.create_index('idx_sessions_expires_at', 'user_sessions', ['expires_at'])
    op.create_index('idx_sessions_is_active', 'user_sessions', ['is_active'])
    
    # Audit Log table
    op.create_table(
        'audit_logs',
        sa.Column('id', sa.BigInteger, primary_key=True, autoincrement=True),
        sa.Column('user_id', sa.String(100), sa.ForeignKey('users.id', ondelete='SET NULL')),
        sa.Column('action', sa.String(100), nullable=False),
        sa.Column('resource_type', sa.String(100)),
        sa.Column('resource_id', sa.String(100)),
        sa.Column('ip_address', sa.String(45)),
        sa.Column('user_agent', sa.Text),
        sa.Column('details', postgresql.JSONB, server_default='{}'),
        sa.Column('timestamp', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('NOW()')),
    )
    
    # Indexes for audit logs
    op.create_index('idx_audit_user_id', 'audit_logs', ['user_id'])
    op.create_index('idx_audit_action', 'audit_logs', ['action'])
    op.create_index('idx_audit_timestamp', 'audit_logs', ['timestamp'])
    op.create_index('idx_audit_resource', 'audit_logs', ['resource_type', 'resource_id'])


def downgrade() -> None:
    """Drop all tables"""
    op.drop_table('audit_logs')
    op.drop_table('user_sessions')
    op.drop_table('audio_collections')
    op.drop_table('oauth_accounts')
    op.drop_table('api_keys')
    op.drop_table('users')
    
    # Drop extensions (optional, might be used by other schemas)
    # op.execute('DROP EXTENSION IF EXISTS vector')
    # op.execute('DROP EXTENSION IF EXISTS pg_trgm')
    # op.execute('DROP EXTENSION IF EXISTS btree_gin')
