# app/routes/admin/__init__.py

from flask import Blueprint
from flask_admin import Admin
from .views.base import MyAdminIndexView


bp = Blueprint('admin_auth', __name__, url_prefix='/admin')

# 1. Create the custom index view for your dashboard
index_view = MyAdminIndexView(
    name='Dashboard',
    template='admin/dashboard.html',
    url='/admin'
)

# 2. Initialize the Admin object
admin = Admin(
    name='Tucson Golden Doodles',
    index_view=index_view,
    url='/'
)

# 3. Explicitly set the base_template for the admin interface
admin.base_template = 'admin/base_admin.html'

# This import must come AFTER the admin object is defined
from . import routes