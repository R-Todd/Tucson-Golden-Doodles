import pytest
from app import create_app, db as _db
from config import TestingConfig

@pytest.fixture(scope='session')
def app():
    """Create and configure a new app instance for each test session."""
    app = create_app(TestingConfig)
    app_context = app.app_context()
    app_context.push()
    yield app
    app_context.pop()

@pytest.fixture(scope='function')
def db(app):
    """
    Create a fresh database for each test function.
    This ensures test isolation.
    """
    _db.app = app
    _db.create_all()
    yield _db
    _db.session.remove()
    _db.drop_all()

@pytest.fixture(scope='function')
def client(app):
    """A test client for the app."""
    return app.test_client()