# app/routes/admin/__init__.py

from flask import Blueprint
from flask_admin import Admin
from .views import MyAdminIndexView

bp = Blueprint('admin_auth', __name__, url_prefix='/admin')

# Initialize the Flask-Admin extension
# We're telling Flask-Admin to use the Bootstrap 4 template mode,
# which is much more modern and will fix the core layout issues.
admin = Admin(
    name='Tucson Golden Doodles Admin',
    template_mode='bootstrap4',  # <-- added line for admin header
    index_view=MyAdminIndexView(url='/admin'),
    base_template='admin/base_admin.html'
)

# This import must come AFTER the admin object is defined.
from . import routes
