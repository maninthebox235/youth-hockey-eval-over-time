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
    # Use batch mode to handle SQLite constraints
    with op.batch_alter_table('players') as batch_op:
        # Only add columns if they don't exist
        # Skating skills
        batch_op.add_column(sa.Column('edge_control', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('agility', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('backward_skating', sa.Integer(), nullable=True))

        # Puck handling
        batch_op.add_column(sa.Column('puck_control', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('passing_accuracy', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('receiving', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('stick_protection', sa.Integer(), nullable=True))

        # Hockey IQ
        batch_op.add_column(sa.Column('decision_making', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('game_awareness', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('hockey_sense', sa.Integer(), nullable=True))

        # Shooting
        batch_op.add_column(sa.Column('wrist_shot', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('slap_shot', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('one_timer', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('shot_accuracy', sa.Integer(), nullable=True))

        # Defense
        batch_op.add_column(sa.Column('gap_control', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('physicality', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('shot_blocking', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('breakout_passes', sa.Integer(), nullable=True))

        # Goalie specific
        batch_op.add_column(sa.Column('save_technique', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('rebound_control', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('puck_handling', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('recovery', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('glove_saves', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('blocker_saves', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('post_integration', sa.Integer(), nullable=True))

    # Initialize with default values
    op.execute(text("""
        UPDATE players 
        SET edge_control = 0, agility = 0, backward_skating = 0,
            puck_control = 0, passing_accuracy = 0, receiving = 0, stick_protection = 0,
            decision_making = 0, game_awareness = 0, hockey_sense = 0,
            wrist_shot = 0, slap_shot = 0, one_timer = 0, shot_accuracy = 0,
            gap_control = 0, physicality = 0, shot_blocking = 0, breakout_passes = 0,
            save_technique = 0, rebound_control = 0, puck_handling = 0, recovery = 0,
            glove_saves = 0, blocker_saves = 0, post_integration = 0
        WHERE edge_control IS NULL
    """))

def downgrade():
    # Don't drop columns in downgrade to preserve data
    pass