# app/routes/admin/forms/parent_forms.py

from flask_wtf import FlaskForm
from wtforms import (
    StringField, BooleanField, SelectField, DateField, FloatField, TextAreaField
)
from wtforms.fields import FileField
from wtforms.validators import DataRequired, Optional
from wtforms_sqlalchemy.fields import QuerySelectField
from app.models import ParentRole, Breed

def breed_query():
  """A callable function to provide the query for the breed dropdown."""
  return Breed.query.order_by(Breed.name)

class ParentForm(FlaskForm):
    """Custom form for creating and editing Parent records."""
    name = StringField('Name', validators=[DataRequired()])
    role = SelectField(
        'Role',
        choices=[(role.name, role.value) for role in ParentRole],
        coerce=lambda x: ParentRole[x] if isinstance(x, str) else x,
        validators=[DataRequired()]
    )
    
    # --- THIS IS THE CHANGE ---
    # The 'breed' field is now a QuerySelectField, which creates a dropdown
    # populated with all the breeds from the database.
    breed = QuerySelectField(
        'Breed',
        query_factory=breed_query,
        get_label='name',
        allow_blank=True,
        blank_text='-- Select a Breed --'
    )
    
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