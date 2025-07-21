# app/routes/admin/__init__.py

from flask import Blueprint
from flask_admin import Admin
# This now needs to import from the new views package
from .views import MyAdminIndexView

bp = Blueprint('admin_auth', __name__, url_prefix='/admin')

# -- ---
# The `base_template` argument has been removed.
admin = Admin(
    name='Tucson Golden Doodles Admin',
    #template_mode='bootstrap3',
    index_view=MyAdminIndexView(url='/admin')
)

# This import must come AFTER the admin object is defined.
from . import routes