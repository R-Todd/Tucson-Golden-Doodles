# app/routes/admin/__init__.py

from flask import Blueprint
from flask_admin import Admin
from .views.base import MyAdminIndexView

bp = Blueprint('admin_auth', __name__, url_prefix='/admin')

# Initialize the Flask-Admin extension with your settings
# 'template_mode' is supported in Flask-Admin 2.0.0a4 and later
admin = Admin(
    name='Tucson Golden Doodles Admin',
    template_mode='bootstrap4', # This argument requires Flask-Admin 2.x
    index_view=MyAdminIndexView(url='/admin'),
    base_template='admin/base_admin.html'
)

# This import must come AFTER the admin object is defined.
from . import routes