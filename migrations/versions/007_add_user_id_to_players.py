"""Add user_id to players

Revision ID: 007
Revises: 006
Create Date: 2025-03-16

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '007'
down_revision = '006'
branch_labels = None
depends_on = None


def upgrade():
    # Add user_id column to players table
    op.add_column('players', sa.Column('user_id', sa.Integer(), nullable=True))
    op.create_foreign_key(None, 'players', 'users', ['user_id'], ['id'])


def downgrade():
    # Remove user_id column from players table
    op.drop_constraint(None, 'players', type_='foreignkey')
    op.drop_column('players', 'user_id')