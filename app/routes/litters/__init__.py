from flask import Blueprint

bp = Blueprint("litters", __name__, url_prefix="/litters")

from . import routes  # noqa: E402,F401