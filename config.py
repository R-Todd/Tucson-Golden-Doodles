import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

class Config:
    """Set Flask configuration variables from environment variables."""
    SECRET_KEY = os.environ.get('SECRET_KEY') 
    # Throw error if the secret key is not found
    if not SECRET_KEY:
        raise ValueError("No Secret_Key set for Flask application.")
    
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class TestingConfig(Config):
    """Configuration for testing."""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'  # Use in-memory SQLite database
    WTF_CSRF_ENABLED = False  # Disable CSRF forms in tests for simplicity
    SECRET_KEY = 'test-secret-key'
