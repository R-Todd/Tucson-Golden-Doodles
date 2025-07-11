from flask import Flask
from flask_migrate import Migrate
from config import Config
from datetime import datetime, timezone

from app.models import db # Import the db instance from the new models package

migrate = Migrate()

def create_app(config_class=Config):
    """Application factory function."""
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)

    @app.context_processor
    def inject_utility_vars():
        """Injects variables into all templates."""
        from app.models import SiteMeta # Update the import path for SiteMeta
        return dict(
            site_meta=SiteMeta.query.first(),
            now=datetime.now(timezone.utc)
        )

    # Register the new parents blueprint
    from app.parents import bp as parents_bp
    app.register_blueprint(parents_bp)
    
    # Register the new puppies blueprint
    from app.puppies import bp as puppies_bp
    app.register_blueprint(puppies_bp)
    
    # Register the main blueprint for homepage, etc.
    from app.main import bp as main_bp
    app.register_blueprint(main_bp)

    return app