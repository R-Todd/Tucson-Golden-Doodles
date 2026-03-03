from flask import abort, render_template
from sqlalchemy.orm import selectinload

from app.routes.litters import bp
from app.models import Litter, PuppyStatus


@bp.route("/")
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

    # Only show CURRENT litters on the public Litters page
    current_litters = [l for l in litters if not l.is_past]

    return render_template(
        "litters.html",
        title="Current Litters",
        litters=current_litters,
        PuppyStatus=PuppyStatus
    )


@bp.route("/<int:litter_id>")
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
        "litter_detail.html",
        title=litter.display_label,
        litter=litter,
        PuppyStatus=PuppyStatus
    )