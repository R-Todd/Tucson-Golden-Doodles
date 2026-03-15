from flask import abort, render_template
from sqlalchemy.orm import selectinload

from app.routes.puppies import bp
from app.models import Litter, Puppy, PuppyStatus


@bp.route('/')
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

@bp.route('/available-puppies')
def available_puppies():
    """Renders a global list of AVAILABLE puppies, ordered by litter birth date."""

    puppies = (
        Puppy.query
        .options(
            selectinload(Puppy.litter).selectinload(Litter.mother),
            selectinload(Puppy.litter).selectinload(Litter.father)
        )
        .join(Puppy.litter)
        .filter(Puppy.status == PuppyStatus.AVAILABLE)
        .order_by(Litter.birth_date.desc(), Puppy.name.asc())
        .all()
    )

    return render_template(
        'available_puppies.html',
        title='Available Puppies',
        puppies=puppies,
        PuppyStatus=PuppyStatus
    )