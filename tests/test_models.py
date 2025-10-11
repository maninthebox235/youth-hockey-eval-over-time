"""Tests for database models."""

import pytest
from datetime import datetime
from database.models import User, Player, Team, TeamMembership, CoachFeedback


class TestUserModel:
    """Tests for the User model."""

    def test_create_user(self, db_session):
        """Test creating a new user."""
        user = User(
            username="newuser", email="newuser@example.com", name="New User"
        )
        user.set_password("password123")
        db_session.add(user)
        db_session.commit()

        assert user.id is not None
        assert user.username == "newuser"
        assert user.check_password("password123")
        assert not user.check_password("wrongpassword")

    def test_user_admin_flag(self, db_session):
        """Test user admin flag."""
        admin = User(
            username="admin", email="admin@example.com", name="Admin", is_admin=True
        )
        admin.set_password("admin123")
        db_session.add(admin)
        db_session.commit()

        assert admin.is_admin is True

    def test_auth_token_generation(self, sample_user):
        """Test authentication token generation and verification."""
        token = sample_user.get_auth_token()
        assert token is not None

        verified_user = User.verify_auth_token(token)
        assert verified_user.id == sample_user.id


class TestPlayerModel:
    """Tests for the Player model."""

    def test_create_player(self, db_session, sample_user):
        """Test creating a new player."""
        player = Player(
            name="New Player",
            age=14,
            position="Defense",
            skating_speed=70,
            shooting_accuracy=65,
            user_id=sample_user.id,
        )
        db_session.add(player)
        db_session.commit()

        assert player.id is not None
        assert player.name == "New Player"
        assert player.position == "Defense"
        assert player.age_group == "U14"

    def test_player_age_group_calculation(self, db_session, sample_user):
        """Test age group calculation."""
        player_10 = Player(
            name="Player 10", age=10, position="Forward", user_id=sample_user.id
        )
        player_11 = Player(
            name="Player 11", age=11, position="Forward", user_id=sample_user.id
        )
        player_12 = Player(
            name="Player 12", age=12, position="Forward", user_id=sample_user.id
        )

        assert player_10.age_group == "U10"
        assert player_11.age_group == "U10"
        assert player_12.age_group == "U12"

    def test_goalie_specific_stats(self, db_session, sample_user):
        """Test goalie-specific statistics."""
        goalie = Player(
            name="Test Goalie",
            age=15,
            position="Goalie",
            save_percentage=92.5,
            reaction_time=85,
            user_id=sample_user.id,
        )
        db_session.add(goalie)
        db_session.commit()

        assert goalie.position == "Goalie"
        assert goalie.save_percentage == 92.5
        assert goalie.reaction_time == 85


class TestTeamModel:
    """Tests for the Team model."""

    def test_create_team(self, db_session, sample_user):
        """Test creating a new team."""
        team = Team(
            name="Hawks", age_group="U14", user_id=sample_user.id, games_played=15
        )
        db_session.add(team)
        db_session.commit()

        assert team.id is not None
        assert team.name == "Hawks"
        assert team.age_group == "U14"

    def test_team_membership(self, db_session, sample_player, sample_team):
        """Test adding a player to a team."""
        membership = TeamMembership(
            player_id=sample_player.id,
            team_id=sample_team.id,
            position_in_team="Forward",
            is_active=True,
        )
        db_session.add(membership)
        db_session.commit()

        assert membership.id is not None
        assert membership.player_id == sample_player.id
        assert membership.team_id == sample_team.id


class TestCoachFeedback:
    """Tests for the CoachFeedback model."""

    def test_create_feedback(self, db_session, sample_player, sample_user):
        """Test creating coach feedback."""
        feedback = CoachFeedback(
            player_id=sample_player.id,
            coach_id=sample_user.id,
            coach_name=sample_user.name,
            date=datetime.now(),
            skating_stride=4,
            skating_speed=3,
            edge_control=4,
            shooting_power=3,
            shooting_accuracy=4,
        )
        db_session.add(feedback)
        db_session.commit()

        assert feedback.id is not None
        assert feedback.player_id == sample_player.id
        assert feedback.skating_stride == 4
