from flask import Blueprint

# The name 'parents' is used for url_for, e.g., url_for('parents.list_parents')
bp = Blueprint('parents', __name__)

from app.parents import routes