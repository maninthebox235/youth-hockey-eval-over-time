"""Add coach feedback ratings

Revision ID: 008
Revises: 007
Create Date: 2025-03-16

"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '008'
down_revision = '007'
branch_labels = None
depends_on = None

def upgrade():
    # Add new rating columns to coach_feedback table
    op.add_column('coach_feedback', sa.Column('skating_speed_rating', sa.Integer(), nullable=True))
    op.add_column('coach_feedback', sa.Column('backward_skating_rating', sa.Integer(), nullable=True))
    op.add_column('coach_feedback', sa.Column('agility_rating', sa.Integer(), nullable=True))
    op.add_column('coach_feedback', sa.Column('edge_control_rating', sa.Integer(), nullable=True))
    
    op.add_column('coach_feedback', sa.Column('puck_control_rating', sa.Integer(), nullable=True))
    op.add_column('coach_feedback', sa.Column('passing_accuracy_rating', sa.Integer(), nullable=True))
    op.add_column('coach_feedback', sa.Column('shooting_accuracy_rating', sa.Integer(), nullable=True))
    op.add_column('coach_feedback', sa.Column('receiving_rating', sa.Integer(), nullable=True))
    op.add_column('coach_feedback', sa.Column('stick_protection_rating', sa.Integer(), nullable=True))
    
    op.add_column('coach_feedback', sa.Column('hockey_sense_rating', sa.Integer(), nullable=True))
    op.add_column('coach_feedback', sa.Column('decision_making_rating', sa.Integer(), nullable=True))
    op.add_column('coach_feedback', sa.Column('game_awareness_rating', sa.Integer(), nullable=True))
    
    op.add_column('coach_feedback', sa.Column('compete_level_rating', sa.Integer(), nullable=True))
    op.add_column('coach_feedback', sa.Column('offensive_ability_rating', sa.Integer(), nullable=True))
    op.add_column('coach_feedback', sa.Column('defensive_ability_rating', sa.Integer(), nullable=True))
    op.add_column('coach_feedback', sa.Column('net_front_rating', sa.Integer(), nullable=True))
    op.add_column('coach_feedback', sa.Column('gap_control_rating', sa.Integer(), nullable=True))
    
    op.add_column('coach_feedback', sa.Column('recovery_rating', sa.Integer(), nullable=True))
    op.add_column('coach_feedback', sa.Column('puck_handling_rating', sa.Integer(), nullable=True))
    op.add_column('coach_feedback', sa.Column('communication_rating', sa.Integer(), nullable=True))
    
    # Make sure teamwork_rating is nullable
    op.alter_column('coach_feedback', 'teamwork_rating', nullable=True)

def downgrade():
    # Remove the newly added columns
    op.drop_column('coach_feedback', 'skating_speed_rating')
    op.drop_column('coach_feedback', 'backward_skating_rating')
    op.drop_column('coach_feedback', 'agility_rating')
    op.drop_column('coach_feedback', 'edge_control_rating')
    
    op.drop_column('coach_feedback', 'puck_control_rating')
    op.drop_column('coach_feedback', 'passing_accuracy_rating')
    op.drop_column('coach_feedback', 'shooting_accuracy_rating')
    op.drop_column('coach_feedback', 'receiving_rating')
    op.drop_column('coach_feedback', 'stick_protection_rating')
    
    op.drop_column('coach_feedback', 'hockey_sense_rating')
    op.drop_column('coach_feedback', 'decision_making_rating')
    op.drop_column('coach_feedback', 'game_awareness_rating')
    
    op.drop_column('coach_feedback', 'compete_level_rating')
    op.drop_column('coach_feedback', 'offensive_ability_rating')
    op.drop_column('coach_feedback', 'defensive_ability_rating')
    op.drop_column('coach_feedback', 'net_front_rating')
    op.drop_column('coach_feedback', 'gap_control_rating')
    
    op.drop_column('coach_feedback', 'recovery_rating')
    op.drop_column('coach_feedback', 'puck_handling_rating')
    op.drop_column('coach_feedback', 'communication_rating')