from flask import render_template
from sqlalchemy.orm import selectinload

from app.routes.puppies import bp
from app.models import Litter, PuppyStatus


@bp.route('/puppies')
def list_puppies():
    """
    Renders the page with all puppies, grouped by Litter model.
    Newest litters appear first.
    """

    litters = (
        Litter.query
        .options(
            selectinload(Litter.puppies),
            selectinload(Litter.mother),
            selectinload(Litter.father)
        )
        .order_by(Litter.birth_date.desc())
        .all()
    )

    # Sort puppies inside each litter by name for consistent display
    for litter in litters:
        litter.puppies.sort(key=lambda p: p.name or "")

    return render_template(
        'puppies.html',
        title='Our Puppies',
        litters=litters,
        PuppyStatus=PuppyStatus
    )
