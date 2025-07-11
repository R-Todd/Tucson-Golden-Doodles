from flask import Blueprint

bp = Blueprint('admin_auth', __name__, url_prefix='/admin')

from . import routes