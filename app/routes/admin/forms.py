# app/routes/admin/forms.py

from flask_wtf import FlaskForm
from wtforms import (
    StringField, BooleanField, SelectField, DateField, FloatField, TextAreaField
)
from wtforms.fields import FileField
from wtforms.validators import DataRequired, Optional
from wtforms_sqlalchemy.fields import QuerySelectField
from app.models import Puppy, ParentRole
from collections import OrderedDict
from itertools import groupby

# --- Announcement Banner Form  ---

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
    
    sub_text = StringField(
        'Sub Text', 
        validators=[DataRequired()],
        description="Use placeholders to automatically include litter info. Available placeholders: {mom_name}, {dad_name}, {birth_date}"
    )
    
    button_text = StringField('Button Text', validators=[DataRequired()])
    
    featured_puppy = QuerySelectField(
        'Featured Litter',
        query_factory=get_litters,
        get_label=get_litter_label,
        allow_blank=True,
        blank_text='-- Select a Litter --',
        description="Select a litter to feature in the banner."
    )

# --- Parent Form (New) ---

class ParentForm(FlaskForm):
    """Custom form for creating and editing Parent records."""
    name = StringField('Name', validators=[DataRequired()])
    role = SelectField(
        'Role',
        choices=[(role.name, role.value) for role in ParentRole],
        coerce=lambda x: ParentRole[x] if isinstance(x, str) else x,
        validators=[DataRequired()]
    )
    breed = StringField('Breed')
    birth_date = DateField('Birth Date', validators=[Optional()])
    weight_kg = FloatField('Weight (kg)', validators=[Optional()])
    height_cm = FloatField('Height (cm)', validators=[Optional()])
    is_active = BooleanField('Is Active', default=True)
    is_guardian = BooleanField('Is Guardian Home', default=False)
    description = TextAreaField('Description')

    # Image Upload Fields
    image_upload = FileField('Upload New Main Image')
    alternate_image_upload_1 = FileField('Upload Alternate Image 1')
    alternate_image_upload_2 = FileField('Upload Alternate Image 2')
    alternate_image_upload_3 = FileField('Upload Alternate Image 3')
    alternate_image_upload_4 = FileField('Upload Alternate Image 4')