# app/routes/admin/__init__.py

from flask import Blueprint
from flask_admin import Admin
# --- THIS IS THE FIX ---
# Import MyAdminIndexView directly from its source file (.views.base)
# to break the circular dependency.
from .views.base import MyAdminIndexView

bp = Blueprint('admin_auth', __name__, url_prefix='/admin')

# Initialize the Flask-Admin extension with your settings
admin = Admin(
    name='Tucson Golden Doodles Admin',
    template_mode='bootstrap4',
    index_view=MyAdminIndexView(url='/admin'),
    base_template='admin/base_admin.html'
)

# This import must come AFTER the admin object is defined.
from . import routes