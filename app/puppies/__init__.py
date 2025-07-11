from flask import Blueprint

# The name 'puppies' is used for url_for, e.g., url_for('puppies.list_puppies')
bp = Blueprint('puppies', __name__)

from app.puppies import routes