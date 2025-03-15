"""Add user management

Revision ID: 004
Revises: 003
Create Date: 2024-03-15 10:30:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '004'
down_revision = '003'
branch_labels = None
depends_on = None

def upgrade():
    # Create users table
    op.create_table('users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('email', sa.String(length=120), nullable=False),
        sa.Column('password_hash', sa.String(length=256), nullable=True),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('is_admin', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('last_login', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email')
    )
    
    # Add coach_id to coach_feedback table
    op.add_column('coach_feedback',
        sa.Column('coach_id', sa.Integer(), nullable=True)
    )
    op.create_foreign_key(
        'fk_coach_feedback_coach_id_users',
        'coach_feedback', 'users',
        ['coach_id'], ['id']
    )

def downgrade():
    op.drop_constraint('fk_coach_feedback_coach_id_users', 'coach_feedback', type_='foreignkey')
    op.drop_column('coach_feedback', 'coach_id')
    op.drop_table('users')
