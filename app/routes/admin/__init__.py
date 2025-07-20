# app/routes/admin/__init__.py

from flask import Blueprint
from flask_admin import Admin
# Import the MyAdminIndexView we just moved
from .views import MyAdminIndexView

# --- Blueprint Registration ---
# This blueprint handles the routes for admin authentication (login/logout).
# The 'url_prefix' ensures all routes in this blueprint start with /admin.
bp = Blueprint('admin_auth', __name__, url_prefix='/admin')


# --- Flask-Admin Registration ---
# This is the central registration point for the Flask-Admin extension.
# We create the 'admin' object here, and it will be initialized with the
# Flask app later in the main application factory.
admin = Admin(
    name='Tucson Golden Doodles Admin',
    template_mode='bootstrap3',
    # We pass our custom, authentication-aware index view to Flask-Admin.
    # The url='/admin' is important because it sets the root URL for the admin interface,
    # distinguishing it from the blueprint's prefix if they were different.
    index_view=MyAdminIndexView(url='/admin'),
    # This points Flask-Admin to your custom base template.
    base_template='admin/base_admin.html'
)

# This import is now safe. It comes *after* the admin object is created.
# It will import the routes.py file, which in turn will use the 'admin' and 'bp'
# objects we just defined here to attach the model views and routes.
from . import routes