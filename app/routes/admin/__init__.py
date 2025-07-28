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

# 2. Initialize the Admin object, passing it the custom index view
admin = Admin(
    name='Tucson Golden Doodles Admin',
    index_view=index_view,
    url='/'
)

# 3. Set the base_template on the created instance
# This is the key step to make your custom layout load.
admin.base_template = 'admin/base_admin.html'

# This import must come AFTER the admin object is defined
from . import routes