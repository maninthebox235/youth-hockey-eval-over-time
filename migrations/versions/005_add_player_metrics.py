
"""add player metrics

Revision ID: 005
Revises: 004
Create Date: 2025-03-16

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import text

# revision identifiers
revision = '005'
down_revision = '004'
branch_labels = None
depends_on = None

def upgrade():
    # Get all existing columns to avoid adding duplicates
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    columns = inspector.get_columns('players')
    existing_columns = [column['name'] for column in columns]
    
    # Use batch mode to handle SQLite constraints if needed
    with op.batch_alter_table('players') as batch_op:
        # Skating skills
        if 'edge_control' not in existing_columns:
            batch_op.add_column(sa.Column('edge_control', sa.Float(), nullable=True))
        if 'agility' not in existing_columns:
            batch_op.add_column(sa.Column('agility', sa.Float(), nullable=True))
        if 'backward_skating' not in existing_columns:
            batch_op.add_column(sa.Column('backward_skating', sa.Float(), nullable=True))

        # Puck handling
        if 'puck_control' not in existing_columns:
            batch_op.add_column(sa.Column('puck_control', sa.Float(), nullable=True))
        if 'passing_accuracy' not in existing_columns:
            batch_op.add_column(sa.Column('passing_accuracy', sa.Float(), nullable=True))
        if 'receiving' not in existing_columns:
            batch_op.add_column(sa.Column('receiving', sa.Float(), nullable=True))
        if 'stick_protection' not in existing_columns:
            batch_op.add_column(sa.Column('stick_protection', sa.Float(), nullable=True))

        # Hockey IQ
        if 'decision_making' not in existing_columns:
            batch_op.add_column(sa.Column('decision_making', sa.Float(), nullable=True))
        if 'game_awareness' not in existing_columns:
            batch_op.add_column(sa.Column('game_awareness', sa.Float(), nullable=True))
        if 'hockey_sense' not in existing_columns:
            batch_op.add_column(sa.Column('hockey_sense', sa.Float(), nullable=True))

        # Shooting
        if 'wrist_shot' not in existing_columns:
            batch_op.add_column(sa.Column('wrist_shot', sa.Float(), nullable=True))
        if 'slap_shot' not in existing_columns:
            batch_op.add_column(sa.Column('slap_shot', sa.Float(), nullable=True))
        if 'one_timer' not in existing_columns:
            batch_op.add_column(sa.Column('one_timer', sa.Float(), nullable=True))
        if 'shot_accuracy' not in existing_columns:
            batch_op.add_column(sa.Column('shot_accuracy', sa.Float(), nullable=True))
            
        # Defense specific
        if 'gap_control' not in existing_columns:
            batch_op.add_column(sa.Column('gap_control', sa.Float(), nullable=True))
        if 'physicality' not in existing_columns:
            batch_op.add_column(sa.Column('physicality', sa.Float(), nullable=True))
        if 'shot_blocking' not in existing_columns:
            batch_op.add_column(sa.Column('shot_blocking', sa.Float(), nullable=True))
        if 'breakout_passes' not in existing_columns:
            batch_op.add_column(sa.Column('breakout_passes', sa.Float(), nullable=True))
            
        # Goalie specific metrics that weren't already added
        if 'save_technique' not in existing_columns:
            batch_op.add_column(sa.Column('save_technique', sa.Float(), nullable=True))
        if 'rebound_control' not in existing_columns:
            batch_op.add_column(sa.Column('rebound_control', sa.Float(), nullable=True))
        if 'puck_handling' not in existing_columns:
            batch_op.add_column(sa.Column('puck_handling', sa.Float(), nullable=True))
        if 'recovery' not in existing_columns:
            batch_op.add_column(sa.Column('recovery', sa.Float(), nullable=True))
        if 'glove_saves' not in existing_columns:
            batch_op.add_column(sa.Column('glove_saves', sa.Float(), nullable=True))
        if 'blocker_saves' not in existing_columns:
            batch_op.add_column(sa.Column('blocker_saves', sa.Float(), nullable=True))
        if 'post_integration' not in existing_columns:
            batch_op.add_column(sa.Column('post_integration', sa.Float(), nullable=True))

def downgrade():
    # Remove all added columns
    with op.batch_alter_table('players') as batch_op:
        # Skating skills
        batch_op.drop_column('edge_control')
        batch_op.drop_column('agility')
        batch_op.drop_column('backward_skating')
        
        # Puck handling
        batch_op.drop_column('puck_control')
        batch_op.drop_column('passing_accuracy')
        batch_op.drop_column('receiving')
        batch_op.drop_column('stick_protection')
        
        # Hockey IQ
        batch_op.drop_column('decision_making')
        batch_op.drop_column('game_awareness')
        batch_op.drop_column('hockey_sense')
        
        # Shooting
        batch_op.drop_column('wrist_shot')
        batch_op.drop_column('slap_shot')
        batch_op.drop_column('one_timer')
        batch_op.drop_column('shot_accuracy')
        
        # Defense specific
        batch_op.drop_column('gap_control')
        batch_op.drop_column('physicality')
        batch_op.drop_column('shot_blocking')
        batch_op.drop_column('breakout_passes')
        
        # Goalie specific
        batch_op.drop_column('save_technique')
        batch_op.drop_column('rebound_control')
        batch_op.drop_column('puck_handling')
        batch_op.drop_column('recovery')
        batch_op.drop_column('glove_saves')
        batch_op.drop_column('blocker_saves')
        batch_op.drop_column('post_integration')
