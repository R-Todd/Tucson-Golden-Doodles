from flask import Blueprint

bp = Blueprint("available_puppies", __name__, url_prefix="/available-puppies")

from . import routes  # noqa: E402,F401