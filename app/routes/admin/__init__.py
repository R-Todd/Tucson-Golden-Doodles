# app/routes/admin/__init__.py

from flask import Blueprint
from flask_admin import Admin
# --- THIS IS THE FIX ---
# Import directly from the 'base' module instead of the 'views' package
# to prevent a circular dependency during initialization.
from .views.base import MyAdminIndexView

bp = Blueprint('admin_auth', __name__, url_prefix='/admin')

# The `admin` object is now created without triggering the import of all other views.
admin = Admin(
    name='Tucson Golden Doodles Admin',
    index_view=MyAdminIndexView(url='/admin')
)

# This import must come AFTER the admin object is defined.
# The 'routes' module will then safely import all the necessary views.
from . import routes