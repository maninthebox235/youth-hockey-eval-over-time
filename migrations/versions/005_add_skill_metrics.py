
"""Add all skill metrics columns to PlayerHistory

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
    # Get all existing columns to avoid adding duplicates
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    columns = inspector.get_columns('player_history')
    existing_columns = [column['name'] for column in columns]
    
    # Additional skater metrics columns
    if 'edge_control' not in existing_columns:
        op.add_column('player_history', sa.Column('edge_control', sa.Float(), nullable=True))
    
    if 'agility' not in existing_columns:
        op.add_column('player_history', sa.Column('agility', sa.Float(), nullable=True))
    
    if 'backward_skating' not in existing_columns:
        op.add_column('player_history', sa.Column('backward_skating', sa.Float(), nullable=True))
    
    if 'puck_control' not in existing_columns:
        op.add_column('player_history', sa.Column('puck_control', sa.Float(), nullable=True))
    
    if 'passing_accuracy' not in existing_columns:
        op.add_column('player_history', sa.Column('passing_accuracy', sa.Float(), nullable=True))
    
    if 'receiving' not in existing_columns:
        op.add_column('player_history', sa.Column('receiving', sa.Float(), nullable=True))
    
    if 'stick_protection' not in existing_columns:
        op.add_column('player_history', sa.Column('stick_protection', sa.Float(), nullable=True))
    
    # Game IQ metrics
    if 'decision_making' not in existing_columns:
        op.add_column('player_history', sa.Column('decision_making', sa.Float(), nullable=True))
    
    if 'game_awareness' not in existing_columns:
        op.add_column('player_history', sa.Column('game_awareness', sa.Float(), nullable=True))
    
    if 'hockey_sense' not in existing_columns:
        op.add_column('player_history', sa.Column('hockey_sense', sa.Float(), nullable=True))
    
    # Forward specific metrics
    if 'wrist_shot' not in existing_columns:
        op.add_column('player_history', sa.Column('wrist_shot', sa.Float(), nullable=True))
    
    if 'slap_shot' not in existing_columns:
        op.add_column('player_history', sa.Column('slap_shot', sa.Float(), nullable=True))
    
    if 'one_timer' not in existing_columns:
        op.add_column('player_history', sa.Column('one_timer', sa.Float(), nullable=True))
    
    if 'shot_accuracy' not in existing_columns:
        op.add_column('player_history', sa.Column('shot_accuracy', sa.Float(), nullable=True))
    
    # Defense specific metrics
    if 'gap_control' not in existing_columns:
        op.add_column('player_history', sa.Column('gap_control', sa.Float(), nullable=True))
    
    if 'physicality' not in existing_columns:
        op.add_column('player_history', sa.Column('physicality', sa.Float(), nullable=True))
    
    if 'shot_blocking' not in existing_columns:
        op.add_column('player_history', sa.Column('shot_blocking', sa.Float(), nullable=True))
    
    if 'breakout_passes' not in existing_columns:
        op.add_column('player_history', sa.Column('breakout_passes', sa.Float(), nullable=True))
    
    # Goalie specific metrics
    if 'save_technique' not in existing_columns:
        op.add_column('player_history', sa.Column('save_technique', sa.Float(), nullable=True))
    
    if 'rebound_control' not in existing_columns:
        op.add_column('player_history', sa.Column('rebound_control', sa.Float(), nullable=True))
    
    if 'puck_handling' not in existing_columns:
        op.add_column('player_history', sa.Column('puck_handling', sa.Float(), nullable=True))
    
    if 'recovery' not in existing_columns:
        op.add_column('player_history', sa.Column('recovery', sa.Float(), nullable=True))
    
    if 'glove_saves' not in existing_columns:
        op.add_column('player_history', sa.Column('glove_saves', sa.Float(), nullable=True))
    
    if 'blocker_saves' not in existing_columns:
        op.add_column('player_history', sa.Column('blocker_saves', sa.Float(), nullable=True))
    
    if 'post_integration' not in existing_columns:
        op.add_column('player_history', sa.Column('post_integration', sa.Float(), nullable=True))


def downgrade():
    # Don't drop columns in downgrade to preserve data
    pass
