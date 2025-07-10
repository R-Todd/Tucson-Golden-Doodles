from flask import render_template
from sqlalchemy.orm import joinedload
from app.parents import bp
from app.models import Parent

@bp.route('/parents')
def list_parents():
    """Renders the page with all parent dogs, ordered by role then name."""
    # Eagerly load the 'images' relationship to avoid N+1 queries in the template.
    # We order by role descending to show 'Mom' before 'Dad'.
    parents = Parent.query.options(
        joinedload(Parent.images)
    ).order_by(Parent.role.desc(), Parent.name).all()
    return render_template('parents.html', parents=parents)