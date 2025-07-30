# app/routes/admin/forms.py

from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField
from wtforms.validators import DataRequired
from wtforms_sqlalchemy.fields import QuerySelectField
from app.models import Puppy
from collections import OrderedDict
from itertools import groupby

def get_litters():
    """
    Queries all puppies and groups them into litters, returning one
    representative puppy from each litter for the dropdown.
    """
    puppies = Puppy.query.order_by(Puppy.birth_date.desc(), Puppy.mom_id, Puppy.dad_id).all()
    
    keyfunc = lambda p: (p.birth_date, p.mom, p.dad)
    
    litters_dict = OrderedDict()
    for key, group in groupby(puppies, key=keyfunc):
        litters_dict[key] = list(group)[0]
        
    return list(litters_dict.values())

def get_litter_label(puppy):
    """Creates the display text for each item in the litter dropdown."""
    if not puppy or not puppy.mom or not puppy.dad:
        return "Invalid Litter"
    return (f"Litter from {puppy.mom.name} & {puppy.dad.name} "
            f"(Born: {puppy.birth_date.strftime('%B %Y')})")


class AnnouncementBannerForm(FlaskForm):
    """Custom form for the Announcement Banner admin view."""
    is_active = BooleanField('Is Active', default=True)
    main_text = StringField('Main Text', validators=[DataRequired()])
    sub_text = StringField('Sub Text', validators=[DataRequired()])
    button_text = StringField('Button Text', validators=[DataRequired()])
    
    featured_puppy = QuerySelectField(
        'Featured Litter',
        query_factory=get_litters,
        get_label=get_litter_label,
        allow_blank=True,
        blank_text='-- Select a Litter --',
        description="Select a litter to feature in the banner."
    )