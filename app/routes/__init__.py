# app/routes/__init__.py
"""
Central blueprint registry.

Benefit: one place to see URL ownership and ensure blueprints are registered
consistently and predictably.
"""

from app.routes.admin import bp as admin_bp
from app.routes.parents import bp as parents_bp
from app.routes.puppies import bp as puppies_bp
from app.routes.main import bp as main_bp
from app.routes.litters import bp as litters_bp

# Keep registration order explicit (matches your existing create_app order)
ALL_BLUEPRINTS = (
    admin_bp,
    parents_bp,
    puppies_bp,
    litters_bp,
    main_bp,
)