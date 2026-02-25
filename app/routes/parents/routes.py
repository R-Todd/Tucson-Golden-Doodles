from flask import abort, render_template
from sqlalchemy.orm import selectinload

from app.routes.parents import bp
from app.models import Litter, Parent, PuppyStatus
from app.models.enums import ParentRole


@bp.route('/')
def list_parents():
    """Renders the Parents index page with moms and dads separated."""
    moms = (
        Parent.query
        .filter(Parent.role == ParentRole.MOM)
        .order_by(Parent.name)
        .all()
    )

    dads = (
        Parent.query
        .filter(Parent.role == ParentRole.DAD)
        .order_by(Parent.name)
        .all()
    )

    return render_template('parents.html', moms=moms, dads=dads)


@bp.route('/<int:parent_id>')
def parent_detail(parent_id):
    """
    Renders a dedicated detail page for a single parent.
    Includes the parent's description and past litters with puppy cards.
    """

    parent = (
        Parent.query
        .options(
            selectinload(Parent.images),

            # Litters where this parent is the mom
            selectinload(Parent.litters_as_mom).selectinload(Litter.puppies),
            selectinload(Parent.litters_as_mom).selectinload(Litter.mother),
            selectinload(Parent.litters_as_mom).selectinload(Litter.father),

            # Litters where this parent is the dad
            selectinload(Parent.litters_as_dad).selectinload(Litter.puppies),
            selectinload(Parent.litters_as_dad).selectinload(Litter.mother),
            selectinload(Parent.litters_as_dad).selectinload(Litter.father),
        )
        .filter(Parent.id == parent_id)
        .first()
    )

    if not parent:
        abort(404)

    # Normalize ordering for display (newest litters first; puppies alphabetically)
    litters = sorted(parent.litters or [], key=lambda l: l.birth_date or 0, reverse=True)
    for litter in litters:
        litter.puppies.sort(key=lambda p: p.name or "")

    return render_template(
        'parent_detail.html',
        parent=parent,
        litters=litters,
        PuppyStatus=PuppyStatus
    )