"""Add game evaluations table

Revision ID: 009
Revises: 008
Create Date: 2025-10-13

"""

from alembic import op
import sqlalchemy as sa

revision = '009'
down_revision = '008'
branch_labels = None
depends_on = None

def upgrade():
    op.create_table(
        'game_evaluations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('team_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('evaluator_name', sa.String(length=100), nullable=False),
        sa.Column('game_date', sa.Date(), nullable=False),
        sa.Column('opponent_name', sa.String(length=100), nullable=False),
        sa.Column('final_score', sa.String(length=20), nullable=True),
        sa.Column('game_location', sa.String(length=100), nullable=True),
        sa.Column('video_filename', sa.String(length=255), nullable=True),
        sa.Column('spacing_support_rating', sa.Integer(), nullable=True),
        sa.Column('forechecking_rating', sa.Integer(), nullable=True),
        sa.Column('backchecking_rating', sa.Integer(), nullable=True),
        sa.Column('breakout_rating', sa.Integer(), nullable=True),
        sa.Column('overall_team_effort_rating', sa.Integer(), nullable=True),
        sa.Column('overall_execution_rating', sa.Integer(), nullable=True),
        sa.Column('strengths_notes', sa.Text(), nullable=True),
        sa.Column('areas_for_improvement', sa.Text(), nullable=True),
        sa.Column('coaching_observations', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['team_id'], ['teams.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

def downgrade():
    op.drop_table('game_evaluations')
