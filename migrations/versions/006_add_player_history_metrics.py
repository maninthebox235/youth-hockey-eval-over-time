"""Add additional player history metrics

Revision ID: 006
Revises: 005
Create Date: 2025-03-16

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '006'
down_revision = '005'
branch_labels = None
depends_on = None


def upgrade():
    # Add skating metrics
    op.add_column('player_history', sa.Column('edge_control', sa.Float(), nullable=True))
    op.add_column('player_history', sa.Column('agility', sa.Float(), nullable=True))
    op.add_column('player_history', sa.Column('backward_skating', sa.Float(), nullable=True))
    
    # Add stickhandling metrics
    op.add_column('player_history', sa.Column('puck_control', sa.Float(), nullable=True))
    op.add_column('player_history', sa.Column('passing_accuracy', sa.Float(), nullable=True))
    op.add_column('player_history', sa.Column('receiving', sa.Float(), nullable=True))
    op.add_column('player_history', sa.Column('stick_protection', sa.Float(), nullable=True))
    
    # Add game IQ metrics
    op.add_column('player_history', sa.Column('decision_making', sa.Float(), nullable=True))
    op.add_column('player_history', sa.Column('game_awareness', sa.Float(), nullable=True))
    op.add_column('player_history', sa.Column('hockey_sense', sa.Float(), nullable=True))
    
    # Add forward specific metrics
    op.add_column('player_history', sa.Column('wrist_shot', sa.Float(), nullable=True))
    op.add_column('player_history', sa.Column('slap_shot', sa.Float(), nullable=True))
    op.add_column('player_history', sa.Column('one_timer', sa.Float(), nullable=True))
    op.add_column('player_history', sa.Column('shot_accuracy', sa.Float(), nullable=True))
    
    # Add defense specific metrics
    op.add_column('player_history', sa.Column('gap_control', sa.Float(), nullable=True))
    op.add_column('player_history', sa.Column('physicality', sa.Float(), nullable=True))
    op.add_column('player_history', sa.Column('shot_blocking', sa.Float(), nullable=True))
    op.add_column('player_history', sa.Column('breakout_passes', sa.Float(), nullable=True))
    
    # Add goalie metrics
    op.add_column('player_history', sa.Column('save_technique', sa.Float(), nullable=True))
    op.add_column('player_history', sa.Column('rebound_control', sa.Float(), nullable=True))
    op.add_column('player_history', sa.Column('puck_handling', sa.Float(), nullable=True))
    op.add_column('player_history', sa.Column('recovery', sa.Float(), nullable=True))
    op.add_column('player_history', sa.Column('glove_saves', sa.Float(), nullable=True))
    op.add_column('player_history', sa.Column('blocker_saves', sa.Float(), nullable=True))
    op.add_column('player_history', sa.Column('post_integration', sa.Float(), nullable=True))


def downgrade():
    # Remove all added columns
    # Skating metrics
    op.drop_column('player_history', 'edge_control')
    op.drop_column('player_history', 'agility')
    op.drop_column('player_history', 'backward_skating')
    
    # Stickhandling metrics
    op.drop_column('player_history', 'puck_control')
    op.drop_column('player_history', 'passing_accuracy')
    op.drop_column('player_history', 'receiving')
    op.drop_column('player_history', 'stick_protection')
    
    # Game IQ metrics
    op.drop_column('player_history', 'decision_making')
    op.drop_column('player_history', 'game_awareness')
    op.drop_column('player_history', 'hockey_sense')
    
    # Forward specific metrics
    op.drop_column('player_history', 'wrist_shot')
    op.drop_column('player_history', 'slap_shot')
    op.drop_column('player_history', 'one_timer')
    op.drop_column('player_history', 'shot_accuracy')
    
    # Defense specific metrics
    op.drop_column('player_history', 'gap_control')
    op.drop_column('player_history', 'physicality')
    op.drop_column('player_history', 'shot_blocking')
    op.drop_column('player_history', 'breakout_passes')
    
    # Goalie metrics
    op.drop_column('player_history', 'save_technique')
    op.drop_column('player_history', 'rebound_control')
    op.drop_column('player_history', 'puck_handling')
    op.drop_column('player_history', 'recovery')
    op.drop_column('player_history', 'glove_saves')
    op.drop_column('player_history', 'blocker_saves')
    op.drop_column('player_history', 'post_integration')