"""Add feedback templates

Revision ID: 003
Revises: 002
Create Date: 2025-03-15 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '003'
down_revision = '002'
branch_labels = None
depends_on = None

def upgrade():
    op.create_table('feedback_templates',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('player_type', sa.String(length=20), nullable=False),
        sa.Column('created_date', sa.DateTime(), nullable=False),
        sa.Column('template_structure', sa.JSON(), nullable=False),
        sa.Column('times_used', sa.Integer(), nullable=True),
        sa.Column('last_used', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )

def downgrade():
    op.drop_table('feedback_templates')
