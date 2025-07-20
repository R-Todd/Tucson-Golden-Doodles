# app/__init__.py

from flask import Flask
from flask_migrate import Migrate
from flask_login import LoginManager
from config import Config
from datetime import datetime, timezone

from app.models import db, User
# --- Key Change ---
# Import the 'admin' object from the now-centralized admin blueprint package.
from app.routes.admin import admin

# Initialize Flask extensions
migrate = Migrate()
login = LoginManager()
# Update the login view to use the new blueprint name
login.login_view = 'admin_auth.login'

def create_app(config_class=Config):
    """Application factory function."""
    app = Flask(__name__)
    app.config.from_object(config_class)

    # --- Extension Registration Method ---
    # The init_app method is the standard way to register Flask extensions
    # within an application factory. It binds the extension to the specific
    # app instance being created.
    db.init_app(app)
    migrate.init_app(app, db)
    login.init_app(app)
    # This line connects our configured 'admin' object to the Flask app.
    admin.init_app(app)

    @login.user_loader
    def load_user(id):
        return User.query.get(int(id))

    @app.context_processor
    def inject_utility_vars():
        """Injects variables into all templates."""
        from app.models import SiteMeta
        return dict(
            site_meta=SiteMeta.query.first(),
            now=datetime.now(timezone.utc)
        )

    # --- Blueprint Registration Method ---
    # The register_blueprint method attaches a blueprint to the application.
    # This makes all the routes defined in the blueprint (like /login) active.
    from app.routes.admin import bp as admin_bp
    app.register_blueprint(admin_bp)

    # Register the new parents blueprint
    from app.routes.parents import bp as parents_bp
    app.register_blueprint(parents_bp)

    # Register the new puppies blueprint
    from app.routes.puppies import bp as puppies_bp
    app.register_blueprint(puppies_bp)

    # Register the main blueprint for homepage, etc.
    from app.routes.main import bp as main_bp
    app.register_blueprint(main_bp)

    return app