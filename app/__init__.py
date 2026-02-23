# app/__init__.py

from datetime import datetime, timezone
import os
from flask import Flask
from flask_caching import Cache
from flask_ckeditor import CKEditor
from flask_login import LoginManager
from flask_migrate import Migrate

from config import Config
from app.models import db, User
from app.routes.admin import admin
from app.utils.template_filters import setup_template_filters

cache = Cache()
migrate = Migrate()
login = LoginManager()
login.login_view = "admin_auth.login"
ckeditor = CKEditor()


def _validate_required_config(app: Flask) -> None:
    """
    Validate required config at app startup.

    - Avoid import-time failures (so CLI tools/migrations can import safely).
    - Fail fast only when running as a real app (not debug, not testing).
    """
    if app.debug or app.testing:
        return

    missing = []

    secret = app.config.get("SECRET_KEY")
    if not secret or str(secret).strip() == "":
        missing.append("SECRET_KEY")

    db_uri = app.config.get("SQLALCHEMY_DATABASE_URI")
    if not db_uri or str(db_uri).strip() == "":
        missing.append("DATABASE_URL")

    # Single-admin credentials (required for production)
    admin_user = os.environ.get("ADMIN_USERNAME")
    admin_pass = os.environ.get("ADMIN_PASSWORD")
    if not admin_user or admin_user.strip() == "":
        missing.append("ADMIN_USERNAME")
    if not admin_pass or admin_pass.strip() == "":
        missing.append("ADMIN_PASSWORD")

    if missing:
        raise RuntimeError(
            "Missing required configuration: "
            + ", ".join(missing)
            + ". Set these environment variables before starting the app."
        )


def create_app(config_class=Config):
    """Application factory function."""
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Validate after config is loaded (never at import time)
    _validate_required_config(app)

    # --- Initialize extensions ---
    db.init_app(app)
    migrate.init_app(app, db)
    login.init_app(app)
    admin.init_app(app)
    cache.init_app(app, config={"CACHE_TYPE": "SimpleCache"})
    ckeditor.init_app(app)

    # Register the custom template filter
    setup_template_filters(app)

    @login.user_loader
    def load_user(id):
        return User.query.get(int(id))

    @app.context_processor
    def inject_utility_vars():
        """Injects variables into all templates."""
        from app.models import SiteDetails

        return dict(site_meta=SiteDetails.query.first(), now=datetime.now(timezone.utc))

    # --- Register Blueprints ---
    from app.routes.admin import bp as admin_bp
    app.register_blueprint(admin_bp)

    from app.routes.parents import bp as parents_bp
    app.register_blueprint(parents_bp)

    from app.routes.puppies import bp as puppies_bp
    app.register_blueprint(puppies_bp)

    from app.routes.main import bp as main_bp
    app.register_blueprint(main_bp)

    return app