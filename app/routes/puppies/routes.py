# app/routes/puppies/routes.py

from flask import render_template
from itertools import groupby
from collections import OrderedDict
from sqlalchemy.orm import joinedload
from app.routes.puppies import bp
from app.models import Puppy, PuppyStatus, Litter

@bp.route('/puppies')
def list_puppies():
    """
    Renders the page with all puppies, grouped by litter.
    With the new architecture, we group by the Litter relationship 
    instead of individual puppy attributes.
    """
    # Eagerly load the Litter and its associated parents (mom and dad)
    # This ensures that calling puppy.litter.mom.name doesn't trigger extra DB hits
    puppies_query = Puppy.query.options(
        joinedload(Puppy.litter).joinedload(Litter.mom),
        joinedload(Puppy.litter).joinedload(Litter.dad)
    ).join(Litter).order_by(Litter.birth_date.desc(), Puppy.name).all()

    # Group puppies by their Litter object
    # We use an OrderedDict to maintain the 'newest birth date first' sorting
    litters = OrderedDict()
    
    # groupby expects the list to be sorted by the key, which our query handles
    for litter, group in groupby(puppies_query, key=lambda p: p.litter):
        litters[litter] = list(group)

    return render_template(
        'puppies.html',
        title='Our Puppies',
        litters=litters,
        PuppyStatus=PuppyStatus  # Pass the enum for status badge styling
    )