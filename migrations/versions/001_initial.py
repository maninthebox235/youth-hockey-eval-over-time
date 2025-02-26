"""Initial migration

Revision ID: 001
Revises: 
Create Date: 2024-02-26 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    # Create teams table
    op.create_table('teams',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('age_group', sa.String(length=10), nullable=False),
        sa.Column('created_date', sa.DateTime(), nullable=False),
        sa.Column('games_played', sa.Integer(), nullable=True),
        sa.Column('wins', sa.Integer(), nullable=True),
        sa.Column('losses', sa.Integer(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )

    # Create players table
    op.create_table('players',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('age', sa.Integer(), nullable=False),
        sa.Column('age_group', sa.String(length=10), nullable=False),
        sa.Column('position', sa.String(length=20), nullable=False),
        sa.Column('join_date', sa.DateTime(), nullable=False),
        sa.Column('skating_speed', sa.Float(), nullable=True),
        sa.Column('shooting_accuracy', sa.Float(), nullable=True),
        sa.Column('games_played', sa.Integer(), nullable=True),
        sa.Column('goals', sa.Integer(), nullable=True),
        sa.Column('assists', sa.Integer(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )

    # Create team_membership table
    op.create_table('team_membership',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('player_id', sa.Integer(), nullable=False),
        sa.Column('team_id', sa.Integer(), nullable=False),
        sa.Column('join_date', sa.DateTime(), nullable=False),
        sa.Column('position_in_team', sa.String(length=20), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.ForeignKeyConstraint(['player_id'], ['players.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['team_id'], ['teams.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

def downgrade():
    op.drop_table('team_membership')
    op.drop_table('players')
    op.drop_table('teams')
