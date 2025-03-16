"""Add assessment notes

Revision ID: 003
Revises: 002
Create Date: 2024-03-16 16:45:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '003'
down_revision = '002'
branch_labels = None
depends_on = None

def upgrade():
    op.add_column('player_history', sa.Column('notes', sa.Text(), nullable=True))

def downgrade():
    op.drop_column('player_history', 'notes')
