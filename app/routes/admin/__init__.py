# app/routes/admin/__init__.py

from flask import Blueprint
from flask_admin import Admin
# Import the custom, authentication-aware index view
from .views import MyAdminIndexView

# --- Blueprint Registration ---
# This blueprint handles the routes for admin authentication (login/logout).
# All routes defined using this 'bp' object will be prefixed with '/admin'.
bp = Blueprint('admin_auth', __name__, url_prefix='/admin')


# --- Flask-Admin Initialization ---
# This creates the central 'admin' object for the entire application.
# It's configured with a custom index view to handle authentication checks.
admin = Admin(
    name='Tucson Golden Doodles Admin',
    template_mode='bootstrap3',
    # Sets the entry point for the admin interface to our custom view.
    # The URL '/admin' is the root for all Flask-Admin generated pages.
    index_view=MyAdminIndexView(url='/admin'),
    # Points to a custom base template for consistent branding.
    base_template='admin/base_admin.html'
)

# --- Import Routes and Views ---
# This import is placed at the bottom to avoid circular dependencies.
# It connects the routing logic from 'routes.py' and the model views
# from 'views.py' to the blueprint and admin objects created above.
from . import routes