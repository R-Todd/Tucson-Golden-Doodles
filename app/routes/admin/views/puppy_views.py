# app/routes/admin/views/puppy_views.py

from flask import request
from flask_admin.contrib.sqla.fields import QuerySelectField
from wtforms import Form, StringField, DateField
from wtforms.fields import SelectField, FileField
from wtforms.validators import DataRequired
from wtforms.widgets import Select # Import Select widget <--- NEW IMPORT
from .base import AdminModelView
from app.models import Parent, ParentRole, PuppyStatus
from app.utils.image_uploader import upload_image

# Define a custom form for Puppy model
class PuppyForm(Form):
    """
    Custom form for the Puppy model to explicitly define fields,
    especially QuerySelectFields for parent relationships.
    """
    name = StringField('Name', validators=[DataRequired(message="This field is required.")])
    birth_date = DateField('Birth Date', format='%Y-%m-%d', validators=[DataRequired(message="This field is required.")])

    mom = QuerySelectField(
        'Mother',
        query_factory=lambda: Parent.query.filter_by(role=ParentRole.MOM).all(),
        get_label='name', # Explicitly ensures 4-tuple (value, label, selected, render_kw)
        allow_blank=False, # Make selection mandatory
        blank_text='-- Select Mother --',
        validators=[DataRequired(message="Please select a mother.")],
        widget=Select() # Explicitly use the basic Select widget <--- NEW LINE
    )
    dad = QuerySelectField(
        'Father',
        query_factory=lambda: Parent.query.filter_by(role=ParentRole.DAD).all(),
        get_label='name', # Explicitly ensures 4-tuple (value, label, selected, render_kw)
        allow_blank=False, # Make selection mandatory
        blank_text='-- Select Father --',
        validators=[DataRequired(message="Please select a father.")],
        widget=Select() # Explicitly use the basic Select widget <--- NEW LINE
    )
    status = SelectField(
        'Status',
        choices=[(s.name, s.value) for s in PuppyStatus],
        coerce=lambda x: PuppyStatus[x] if isinstance(x, str) else x,
        validators=[DataRequired(message="This field is required.")]
    )
    image_upload = FileField('Upload New Main Image')


class PuppyAdminView(AdminModelView):
    """ Custom view for the Puppy model, using a dedicated form. """
    
    # Point Flask-Admin to use the custom PuppyForm
    form = PuppyForm 

    # form_columns can still be used to control the display order of fields
    form_columns = [
        'name', 'birth_date', 'status', 'mom', 'dad', 'image_upload'
    ]
    
    def on_model_change(self, form, model, is_created):
        """ Handle image upload when a Puppy record is saved. """
        file = request.files.get('image_upload')
        if file:
            image_url = upload_image(file, folder='puppies')
            if image_url:
                model.main_image_url = image_url