
"""Add notes column if not exists

Revision ID: 004
Revises: 003
Create Date: 2025-03-16

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '004'
down_revision = '003'
branch_labels = None
depends_on = None


def upgrade():
    # Use SQL to check if column exists first
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    columns = inspector.get_columns('player_history')
    column_names = [column['name'] for column in columns]
    
    if 'notes' not in column_names:
        op.add_column('player_history', sa.Column('notes', sa.Text(), nullable=True))
        print("Added notes column to player_history table")
    else:
        print("notes column already exists in player_history table")


def downgrade():
    # Don't drop the column in downgrade
    pass
