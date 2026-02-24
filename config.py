import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))

# Load .env only if it exists (and never override real environment variables)
dotenv_path = os.path.join(basedir, ".env")
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path, override=False)


class Config:
    """Set Flask configuration variables from environment variables."""

    # Flask-related configurations
    SECRET_KEY = os.environ.get("SECRET_KEY")

    # SQLAlchemy database configurations
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    S3_PRESIGN_EXPIRES = int(os.environ.get("S3_PRESIGN_EXPIRES", 3600))
    S3_URL_CACHE_TTL = int(os.environ.get("S3_URL_CACHE_TTL", 3000))


class TestingConfig(Config):
    """Configuration for testing."""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    WTF_CSRF_ENABLED = False
    SECRET_KEY = "test-secret-key"