"""Pytest configuration and fixtures for the test suite."""

import pytest
import os
from database import db
from app import create_app
from database.models import User, Player, Team


@pytest.fixture(scope="session")
def app():
    """Create application for testing."""
    test_db_url = os.getenv("TEST_DATABASE_URL", "sqlite:///:memory:")

    os.environ["SQLALCHEMY_DATABASE_URI"] = test_db_url
    app = create_app()
    app.config["TESTING"] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = test_db_url
    app.config["WTF_CSRF_ENABLED"] = False

    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture(scope="function")
def client(app):
    """Create a test client for the app."""
    return app.test_client()


@pytest.fixture(scope="function")
def db_session(app):
    """Create a database session for a test."""
    with app.app_context():
        yield db.session
        db.session.rollback()


@pytest.fixture
def sample_user(db_session):
    """Create a sample user for testing."""
    user = User(
        username="testuser",
        email="test@example.com",
        name="Test User",
        is_admin=False,
    )
    user.set_password("testpass123")
    db_session.add(user)
    db_session.commit()
    return user


@pytest.fixture
def sample_player(db_session, sample_user):
    """Create a sample player for testing."""
    player = Player(
        name="Test Player",
        age=12,
        position="Forward",
        skating_speed=75,
        shooting_accuracy=80,
        user_id=sample_user.id,
    )
    db_session.add(player)
    db_session.commit()
    return player


@pytest.fixture
def sample_team(db_session, sample_user):
    """Create a sample team for testing."""
    team = Team(
        name="Test Team", age_group="U12", user_id=sample_user.id, games_played=10
    )
    db_session.add(team)
    db_session.commit()
    return team
