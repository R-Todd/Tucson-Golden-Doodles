from flask import render_template
from sqlalchemy.orm import selectinload

from app.routes.available_puppies import bp
from app.models import Litter, Puppy, PuppyStatus


@bp.route("/")
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
        "available_puppies.html",
        title="Available Puppies",
        puppies=puppies,
        PuppyStatus=PuppyStatus
    )