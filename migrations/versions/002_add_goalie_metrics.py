"""Add goalie metrics

Revision ID: 002
Revises: 001
Create Date: 2024-03-15 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None

def upgrade():
    # Add goalie-specific columns to players table
    op.add_column('players', sa.Column('save_percentage', sa.Float(), nullable=True))
    op.add_column('players', sa.Column('reaction_time', sa.Float(), nullable=True))
    op.add_column('players', sa.Column('positioning', sa.Float(), nullable=True))
    op.add_column('players', sa.Column('goals_against', sa.Integer(), nullable=True))
    op.add_column('players', sa.Column('saves', sa.Integer(), nullable=True))
    
    # Add goalie-specific columns to player_history table
    op.add_column('player_history', sa.Column('save_percentage', sa.Float(), nullable=True))
    op.add_column('player_history', sa.Column('reaction_time', sa.Float(), nullable=True))
    op.add_column('player_history', sa.Column('positioning', sa.Float(), nullable=True))
    op.add_column('player_history', sa.Column('goals_against', sa.Integer(), nullable=True))
    op.add_column('player_history', sa.Column('saves', sa.Integer(), nullable=True))
    
    # Add goalie-specific ratings to coach_feedback table
    op.add_column('coach_feedback', sa.Column('save_technique_rating', sa.Integer(), nullable=True))
    op.add_column('coach_feedback', sa.Column('positioning_rating', sa.Integer(), nullable=True))
    op.add_column('coach_feedback', sa.Column('rebound_control_rating', sa.Integer(), nullable=True))

def downgrade():
    # Remove goalie-specific columns from players table
    op.drop_column('players', 'save_percentage')
    op.drop_column('players', 'reaction_time')
    op.drop_column('players', 'positioning')
    op.drop_column('players', 'goals_against')
    op.drop_column('players', 'saves')
    
    # Remove goalie-specific columns from player_history table
    op.drop_column('player_history', 'save_percentage')
    op.drop_column('player_history', 'reaction_time')
    op.drop_column('player_history', 'positioning')
    op.drop_column('player_history', 'goals_against')
    op.drop_column('player_history', 'saves')
    
    # Remove goalie-specific ratings from coach_feedback table
    op.drop_column('coach_feedback', 'save_technique_rating')
    op.drop_column('coach_feedback', 'positioning_rating')
    op.drop_column('coach_feedback', 'rebound_control_rating')
