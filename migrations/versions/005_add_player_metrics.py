
"""Add player metrics columns

Revision ID: 005
Revises: 004
Create Date: 2025-03-16

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '005'
down_revision = '004'
branch_labels = None
depends_on = None


def upgrade():
    # Add skating metrics
    op.add_column('players', sa.Column('edge_control', sa.Float(), nullable=True))
    op.add_column('players', sa.Column('agility', sa.Float(), nullable=True))
    op.add_column('players', sa.Column('backward_skating', sa.Float(), nullable=True))
    
    # Add stickhandling metrics
    op.add_column('players', sa.Column('puck_control', sa.Float(), nullable=True))
    op.add_column('players', sa.Column('passing_accuracy', sa.Float(), nullable=True))
    op.add_column('players', sa.Column('receiving', sa.Float(), nullable=True))
    op.add_column('players', sa.Column('stick_protection', sa.Float(), nullable=True))
    
    # Add game IQ metrics
    op.add_column('players', sa.Column('decision_making', sa.Float(), nullable=True))
    op.add_column('players', sa.Column('game_awareness', sa.Float(), nullable=True))
    op.add_column('players', sa.Column('hockey_sense', sa.Float(), nullable=True))
    
    # Add forward specific metrics
    op.add_column('players', sa.Column('wrist_shot', sa.Float(), nullable=True))
    op.add_column('players', sa.Column('slap_shot', sa.Float(), nullable=True))
    op.add_column('players', sa.Column('one_timer', sa.Float(), nullable=True))
    op.add_column('players', sa.Column('shot_accuracy', sa.Float(), nullable=True))
    
    # Add defense specific metrics
    op.add_column('players', sa.Column('gap_control', sa.Float(), nullable=True))
    op.add_column('players', sa.Column('physicality', sa.Float(), nullable=True))
    op.add_column('players', sa.Column('shot_blocking', sa.Float(), nullable=True))
    op.add_column('players', sa.Column('breakout_passes', sa.Float(), nullable=True))
    
    # Add goalie metrics
    op.add_column('players', sa.Column('save_technique', sa.Float(), nullable=True))
    op.add_column('players', sa.Column('rebound_control', sa.Float(), nullable=True))
    op.add_column('players', sa.Column('puck_handling', sa.Float(), nullable=True))
    op.add_column('players', sa.Column('recovery', sa.Float(), nullable=True))
    op.add_column('players', sa.Column('glove_saves', sa.Float(), nullable=True))
    op.add_column('players', sa.Column('blocker_saves', sa.Float(), nullable=True))
    op.add_column('players', sa.Column('post_integration', sa.Float(), nullable=True))


def downgrade():
    # Remove all added columns
    # Skating metrics
    op.drop_column('players', 'edge_control')
    op.drop_column('players', 'agility')
    op.drop_column('players', 'backward_skating')
    
    # Stickhandling metrics
    op.drop_column('players', 'puck_control')
    op.drop_column('players', 'passing_accuracy')
    op.drop_column('players', 'receiving')
    op.drop_column('players', 'stick_protection')
    
    # Game IQ metrics
    op.drop_column('players', 'decision_making')
    op.drop_column('players', 'game_awareness')
    op.drop_column('players', 'hockey_sense')
    
    # Forward specific metrics
    op.drop_column('players', 'wrist_shot')
    op.drop_column('players', 'slap_shot')
    op.drop_column('players', 'one_timer')
    op.drop_column('players', 'shot_accuracy')
    
    # Defense specific metrics
    op.drop_column('players', 'gap_control')
    op.drop_column('players', 'physicality')
    op.drop_column('players', 'shot_blocking')
    op.drop_column('players', 'breakout_passes')
    
    # Goalie metrics
    op.drop_column('players', 'save_technique')
    op.drop_column('players', 'rebound_control')
    op.drop_column('players', 'puck_handling')
    op.drop_column('players', 'recovery')
    op.drop_column('players', 'glove_saves')
    op.drop_column('players', 'blocker_saves')
    op.drop_column('players', 'post_integration')
