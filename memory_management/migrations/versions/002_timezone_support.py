"""Add timezone support to all datetime columns

Revision ID: 002
Revises: 001_initial
Create Date: 2025-04-13

"""
from alembic import op
import sqlalchemy as sa
from datetime import datetime, timezone

# revision identifiers
revision = '002'
down_revision = '001_initial'
branch_labels = None
depends_on = None

def upgrade():
    # Helper function to get UTC now
    def get_utc_now():
        return datetime.now(timezone.utc)
    
    # SQLite doesn't support timezone type modification directly
    # For PostgreSQL, we can modify column types
    is_sqlite = op.get_bind().dialect.name == 'sqlite'
    
    if not is_sqlite:
        # Users table
        op.alter_column('users', 'created_at',
                       type_=sa.DateTime(timezone=True),
                       existing_type=sa.DateTime(),
                       postgresql_using='created_at AT TIME ZONE \'UTC\'')
        op.alter_column('users', 'last_interaction',
                       type_=sa.DateTime(timezone=True),
                       existing_type=sa.DateTime(),
                       postgresql_using='last_interaction AT TIME ZONE \'UTC\'')
        
        # UserProfile table
        op.alter_column('user_profiles', 'created_at',
                       type_=sa.DateTime(timezone=True),
                       existing_type=sa.DateTime(),
                       postgresql_using='created_at AT TIME ZONE \'UTC\'')
        op.alter_column('user_profiles', 'updated_at',
                       type_=sa.DateTime(timezone=True),
                       existing_type=sa.DateTime(),
                       postgresql_using='updated_at AT TIME ZONE \'UTC\'')
        
        # Message table
        op.alter_column('messages', 'timestamp',
                       type_=sa.DateTime(timezone=True),
                       existing_type=sa.DateTime(),
                       postgresql_using='timestamp AT TIME ZONE \'UTC\'')
        
        # UserFact table
        op.alter_column('user_facts', 'created_at',
                       type_=sa.DateTime(timezone=True),
                       existing_type=sa.DateTime(),
                       postgresql_using='created_at AT TIME ZONE \'UTC\'')
        op.alter_column('user_facts', 'updated_at',
                       type_=sa.DateTime(timezone=True),
                       existing_type=sa.DateTime(),
                       postgresql_using='updated_at AT TIME ZONE \'UTC\'')
        
        # UserMetrics table
        op.alter_column('user_metrics', 'last_interaction_date',
                       type_=sa.DateTime(timezone=True),
                       existing_type=sa.DateTime(),
                       postgresql_using='last_interaction_date AT TIME ZONE \'UTC\'')
        
        # PermanentMemory table
        op.alter_column('permanent_memories', 'created_at',
                       type_=sa.DateTime(timezone=True),
                       existing_type=sa.DateTime(),
                       postgresql_using='created_at AT TIME ZONE \'UTC\'')
        op.alter_column('permanent_memories', 'last_accessed',
                       type_=sa.DateTime(timezone=True),
                       existing_type=sa.DateTime(),
                       postgresql_using='last_accessed AT TIME ZONE \'UTC\'')
        
        # GlobalContext table
        op.alter_column('global_context', 'created_at',
                       type_=sa.DateTime(timezone=True),
                       existing_type=sa.DateTime(),
                       postgresql_using='created_at AT TIME ZONE \'UTC\'')
        op.alter_column('global_context', 'last_updated',
                       type_=sa.DateTime(timezone=True),
                       existing_type=sa.DateTime(),
                       postgresql_using='last_updated AT TIME ZONE \'UTC\'')

def downgrade():
    # SQLite doesn't support timezone type modification directly
    # For PostgreSQL, we can modify column types back
    is_sqlite = op.get_bind().dialect.name == 'sqlite'
    
    if not is_sqlite:
        # Users table
        op.alter_column('users', 'created_at',
                       type_=sa.DateTime(),
                       existing_type=sa.DateTime(timezone=True))
        op.alter_column('users', 'last_interaction',
                       type_=sa.DateTime(),
                       existing_type=sa.DateTime(timezone=True))
        
        # UserProfile table  
        op.alter_column('user_profiles', 'created_at',
                       type_=sa.DateTime(),
                       existing_type=sa.DateTime(timezone=True))
        op.alter_column('user_profiles', 'updated_at',
                       type_=sa.DateTime(),
                       existing_type=sa.DateTime(timezone=True))
        
        # Message table
        op.alter_column('messages', 'timestamp',
                       type_=sa.DateTime(),
                       existing_type=sa.DateTime(timezone=True))
        
        # UserFact table
        op.alter_column('user_facts', 'created_at',
                       type_=sa.DateTime(),
                       existing_type=sa.DateTime(timezone=True))
        op.alter_column('user_facts', 'updated_at',
                       type_=sa.DateTime(),
                       existing_type=sa.DateTime(timezone=True))
        
        # UserMetrics table
        op.alter_column('user_metrics', 'last_interaction_date',
                       type_=sa.DateTime(),
                       existing_type=sa.DateTime(timezone=True))
        
        # PermanentMemory table
        op.alter_column('permanent_memories', 'created_at',
                       type_=sa.DateTime(),
                       existing_type=sa.DateTime(timezone=True))
        op.alter_column('permanent_memories', 'last_accessed',
                       type_=sa.DateTime(),
                       existing_type=sa.DateTime(timezone=True))
        
        # GlobalContext table
        op.alter_column('global_context', 'created_at',
                       type_=sa.DateTime(),
                       existing_type=sa.DateTime(timezone=True))
        op.alter_column('global_context', 'last_updated',
                       type_=sa.DateTime(),
                       existing_type=sa.DateTime(timezone=True))