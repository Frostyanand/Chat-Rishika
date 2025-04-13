"""Initial database schema

Revision ID: 001
Revises: 
Create Date: 2025-04-13 00:00:00.000000
"""
from typing import Sequence, Union
from datetime import datetime

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    # Create users table
    op.create_table(
        'users',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('username', sa.String(100), unique=True, nullable=True),
        sa.Column('created_at', sa.DateTime, nullable=False, default=datetime.utcnow),
        sa.Column('last_interaction', sa.DateTime, nullable=False, default=datetime.utcnow)
    )

    # Create user_profiles table
    op.create_table(
        'user_profiles',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('user_id', sa.String(36), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('name', sa.String(100), nullable=True),
        sa.Column('timezone', sa.String(50), nullable=True),
        sa.Column('preferences', sa.JSON, nullable=True),
        sa.Column('personality_traits', sa.JSON, nullable=True),
        sa.Column('created_at', sa.DateTime, nullable=False, default=datetime.utcnow),
        sa.Column('updated_at', sa.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    )

    # Create messages table
    op.create_table(
        'messages',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('user_id', sa.String(36), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('role', sa.String(20), nullable=False),
        sa.Column('content', sa.Text, nullable=False),
        sa.Column('timestamp', sa.DateTime, nullable=False, default=datetime.utcnow),
        sa.Column('message_metadata', sa.JSON, nullable=True)
    )

    # Create user_facts table
    op.create_table(
        'user_facts',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('user_id', sa.String(36), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('category', sa.String(100), nullable=False),
        sa.Column('fact', sa.Text, nullable=False),
        sa.Column('source', sa.String(100), nullable=True),
        sa.Column('confidence', sa.Float, nullable=True),
        sa.Column('verified', sa.Boolean, default=False),
        sa.Column('fact_metadata', sa.JSON, nullable=True),
        sa.Column('created_at', sa.DateTime, nullable=False, default=datetime.utcnow),
        sa.Column('last_updated', sa.DateTime, nullable=False, default=datetime.utcnow)
    )

    # Create user_metrics table
    op.create_table(
        'user_metrics',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('user_id', sa.String(36), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('total_messages', sa.Integer, default=0),
        sa.Column('total_interactions', sa.Integer, default=0),
        sa.Column('session_count', sa.Integer, default=0),
        sa.Column('daily_streak', sa.Integer, default=0),
        sa.Column('last_session_date', sa.DateTime, nullable=True),
        sa.Column('total_interaction_time', sa.Integer, default=0),
        sa.Column('average_response_time', sa.Float, nullable=True),
        sa.Column('satisfaction_score', sa.Float, nullable=True),
        sa.Column('custom_metrics', sa.JSON, nullable=True)
    )

    # Create permanent_memories table
    op.create_table(
        'permanent_memories',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('user_id', sa.String(36), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('memory_type', sa.String(50), nullable=False),
        sa.Column('content', sa.Text, nullable=False),
        sa.Column('importance_score', sa.Integer, default=5),
        sa.Column('created_at', sa.DateTime, nullable=False, default=datetime.utcnow),
        sa.Column('last_accessed', sa.DateTime, nullable=True),
        sa.Column('access_count', sa.Integer, default=0),
        sa.Column('related_message_ids', sa.JSON, nullable=True)
    )

    # Create global_context table
    op.create_table(
        'global_context',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('key', sa.String(100), unique=True, nullable=False),
        sa.Column('value', sa.JSON, nullable=True),
        sa.Column('category', sa.String(50), nullable=True),
        sa.Column('created_at', sa.DateTime, nullable=False, default=datetime.utcnow),
        sa.Column('last_updated', sa.DateTime, nullable=False, default=datetime.utcnow)
    )

    # Create indexes
    op.create_index('ix_messages_user_id_timestamp', 'messages', ['user_id', 'timestamp'])
    op.create_index('ix_user_facts_user_id_category', 'user_facts', ['user_id', 'category'])
    op.create_index('ix_global_context_category', 'global_context', ['category'])

def downgrade() -> None:
    # Drop tables in reverse order of creation to handle foreign key constraints
    op.drop_table('global_context')
    op.drop_table('permanent_memories')
    op.drop_table('user_metrics')
    op.drop_table('user_facts')
    op.drop_table('messages')
    op.drop_table('user_profiles')
    op.drop_table('users')