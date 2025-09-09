import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

class Config:
    """Set Flask configuration variables from environment variables."""
    # Flask-related configurations
    SECRET_KEY = os.environ.get('SECRET_KEY')
    # Throw error if the secret key is not found - Replaces hardcoded backup key
    if not SECRET_KEY:
        raise ValueError("No Secret_Key set for Flask application.")
    
    # SQLAlchemy database configurations
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class TestingConfig(Config):
    """Configuration for testing."""
    # Enable testing mode
    TESTING = True
    # Use an in-memory SQLite database for tests
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'  # Use in-memory SQLite database
    WTF_CSRF_ENABLED = False  # Disable CSRF forms in tests for simplicity
    SECRET_KEY = 'test-secret-key'
