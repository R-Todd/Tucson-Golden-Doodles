from flask import abort, render_template
from sqlalchemy.orm import selectinload

from app.routes.puppies import bp
from app.models import Litter, Puppy, PuppyStatus


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


@bp.route('/litters')
def list_litters():
    """Renders a tile/grid view of litters (newest first)."""

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

    # Keep puppy ordering deterministic for templates that pick a cover image
    for litter in litters:
        litter.puppies.sort(key=lambda p: p.name or "")

    return render_template(
        'litters.html',
        title='Current Litters',
        litters=litters,
        PuppyStatus=PuppyStatus
    )


@bp.route('/litters/<int:litter_id>')
def litter_detail(litter_id: int):
    """Renders a single litter detail view with parents + puppy grid."""

    litter = (
        Litter.query
        .options(
            selectinload(Litter.puppies),
            selectinload(Litter.mother),
            selectinload(Litter.father)
        )
        .filter(Litter.id == litter_id)
        .first()
    )

    if litter is None:
        abort(404)

    litter.puppies.sort(key=lambda p: p.name or "")

    return render_template(
        'litter_detail.html',
        title=litter.display_label,
        litter=litter,
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