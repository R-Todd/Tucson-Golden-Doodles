# app/routes/admin/__init__.py

from flask import Blueprint
from flask_admin import Admin
from .views.base import MyAdminIndexView # Keep this import, though not used in simplified Admin init

bp = Blueprint('admin_auth', __name__, url_prefix='/admin')

# Initialize the Flask-Admin extension with bare minimum parameters.
# If this still causes a TypeError, it indicates a very fundamental problem.
admin = Admin(
    name='Tucson Golden Doodles Admin',
    # template_mode='bootstrap4', # Removed in previous step
    # index_view=MyAdminIndexView(url='/admin'), # Temporarily removed
    # base_template='admin/base_admin.html' # Temporarily removed
)

# This import must come AFTER the admin object is defined.
from . import routes