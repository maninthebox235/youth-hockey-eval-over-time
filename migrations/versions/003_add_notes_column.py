
"""add notes column to player_history

Revision ID: 003
Revises: 002
Create Date: 2025-03-16

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '003'
down_revision = '002'
branch_labels = None
depends_on = None

def upgrade():
    # Add notes column to player_history table
    op.add_column('player_history', sa.Column('notes', sa.Text(), nullable=True))

def downgrade():
    # Remove notes column from player_history table
    op.drop_column('player_history', 'notes')
