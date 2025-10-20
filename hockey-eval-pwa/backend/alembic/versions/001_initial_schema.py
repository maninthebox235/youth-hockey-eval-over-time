"""Initial schema

Revision ID: 001
Revises: 
Create Date: 2025-10-20 14:30:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table('users',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('email', sa.String(), nullable=False),
    sa.Column('username', sa.String(), nullable=False),
    sa.Column('hashed_password', sa.String(), nullable=False),
    sa.Column('full_name', sa.String(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('is_active', sa.Boolean(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)
    op.create_index(op.f('ix_users_username'), 'users', ['username'], unique=True)

    op.create_table('teams',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('age_group', sa.String(), nullable=True),
    sa.Column('season', sa.String(), nullable=True),
    sa.Column('coach_id', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['coach_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_teams_id'), 'teams', ['id'], unique=False)

    op.create_table('players',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('jersey_number', sa.Integer(), nullable=True),
    sa.Column('position', sa.String(), nullable=True),
    sa.Column('age_group', sa.String(), nullable=True),
    sa.Column('team_id', sa.Integer(), nullable=True),
    sa.Column('coach_id', sa.Integer(), nullable=False),
    sa.Column('photo_url', sa.Text(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['coach_id'], ['users.id'], ),
    sa.ForeignKeyConstraint(['team_id'], ['teams.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_players_id'), 'players', ['id'], unique=False)

    op.create_table('evaluations',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('player_id', sa.Integer(), nullable=False),
    sa.Column('evaluator_id', sa.Integer(), nullable=False),
    sa.Column('evaluator_name', sa.String(), nullable=False),
    sa.Column('date', sa.DateTime(), nullable=True),
    sa.Column('evaluation_type', sa.String(), nullable=False),
    sa.Column('skating', sa.Integer(), nullable=False),
    sa.Column('shooting', sa.Integer(), nullable=False),
    sa.Column('passing', sa.Integer(), nullable=False),
    sa.Column('puck_handling', sa.Integer(), nullable=False),
    sa.Column('hockey_iq', sa.Integer(), nullable=False),
    sa.Column('physicality', sa.Integer(), nullable=False),
    sa.Column('notes', sa.Text(), nullable=True),
    sa.Column('strengths', sa.Text(), nullable=True),
    sa.Column('areas_for_improvement', sa.Text(), nullable=True),
    sa.ForeignKeyConstraint(['evaluator_id'], ['users.id'], ),
    sa.ForeignKeyConstraint(['player_id'], ['players.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_evaluations_id'), 'evaluations', ['id'], unique=False)

    op.create_table('feedback_templates',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('category', sa.String(), nullable=True),
    sa.Column('text', sa.Text(), nullable=False),
    sa.Column('coach_id', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('times_used', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['coach_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_feedback_templates_id'), 'feedback_templates', ['id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_feedback_templates_id'), table_name='feedback_templates')
    op.drop_table('feedback_templates')
    op.drop_index(op.f('ix_evaluations_id'), table_name='evaluations')
    op.drop_table('evaluations')
    op.drop_index(op.f('ix_players_id'), table_name='players')
    op.drop_table('players')
    op.drop_index(op.f('ix_teams_id'), table_name='teams')
    op.drop_table('teams')
    op.drop_index(op.f('ix_users_username'), table_name='users')
    op.drop_index(op.f('ix_users_id'), table_name='users')
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_table('users')
