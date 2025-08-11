# app/__init__.py

from flask import Flask
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_caching import Cache
from flask_ckeditor import CKEditor
from datetime import datetime, timezone
# ---  ---
from config import Config
# --- END OF FIX ---

from app.models import db, User
from app.routes.admin import admin
from app.utils.template_filters import setup_template_filters

cache = Cache()
migrate = Migrate()
login = LoginManager()
login.login_view = 'admin_auth.login'
# --- INITIALIZE CKEDITOR ---
ckeditor = CKEditor()

def create_app(config_class=Config):
    """Application factory function."""
    app = Flask(__name__)
    app.config.from_object(config_class)

    # --- Initialize extensions ---
    db.init_app(app)
    migrate.init_app(app, db)
    login.init_app(app)
    admin.init_app(app)
    cache.init_app(app, config={'CACHE_TYPE': 'SimpleCache'})
    # --- ADD THIS LINE ---
    ckeditor.init_app(app)
    
    # Register the custom template filter ---
    # This makes the `| s3_url` filter available in all Jinja2 templates
    setup_template_filters(app)

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