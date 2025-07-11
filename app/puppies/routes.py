from flask import render_template
from itertools import groupby
from collections import OrderedDict
from sqlalchemy.orm import joinedload
from app.puppies import bp
from app.models import Puppy, PuppyStatus

@bp.route('/puppies')
def list_puppies():
    """
    Renders the page with all puppies, grouped by litter.
    A litter is defined by its birth date and parents.
    """
    # Eagerly load parent data to avoid N+1 queries in the template
    # Order by birth date descending to show newest litters first.
    puppies_query = Puppy.query.options(
        joinedload(Puppy.mom),
        joinedload(Puppy.dad)
    ).order_by(Puppy.birth_date.desc(), Puppy.name).all()

    # Group puppies by litter in Python using an OrderedDict to maintain sort order
    keyfunc = lambda p: (p.birth_date, p.mom, p.dad)
    litters = OrderedDict((key, list(group)) for key, group in groupby(puppies_query, key=keyfunc))

    return render_template(
        'puppies.html',
        title='Our Puppies',
        litters=litters,
        PuppyStatus=PuppyStatus  # Pass the enum to the template for styling
    )