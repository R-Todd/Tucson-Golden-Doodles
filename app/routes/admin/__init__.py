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
    #template_mode='bootstrap3',
    index_view=MyAdminIndexView(url='/admin')
)

# This import must come AFTER the admin object is defined
from . import routes