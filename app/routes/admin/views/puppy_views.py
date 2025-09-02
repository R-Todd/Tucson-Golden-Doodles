# app/routes/admin/views/puppy_views.py

from flask import request
from flask_wtf import FlaskForm
from wtforms.fields import FileField, SelectField, DateField, StringField
from wtforms.validators import InputRequired, DataRequired
from .base import AdminModelView
from app.models import Parent, ParentRole, PuppyStatus, db
from app.utils.image_uploader import upload_image

class PuppyForm(FlaskForm):
    """Defines the fields and validation for the puppy creation and edit forms."""
    # Name of the puppy
    name = StringField('Name', validators=[DataRequired()])
    # Birth date of the puppy, formatted as YYYY-MM-DD
    birth_date = DateField('Birth Date', validators=[DataRequired()], format='%Y-%m-%d')
    # Current status of the puppy, chosen from PuppyStatus enum
    status = SelectField(
        'Status',
        choices=[(s.name, s.value) for s in PuppyStatus],
        coerce=lambda x: PuppyStatus[x] if isinstance(x, str) else x,
        validators=[DataRequired()]
    )
    # ID of the mother, linked to Parent model
    mom_id = SelectField('Mother', coerce=int, validators=[InputRequired(message="Please select a mother.")])
    # ID of the father, linked to Parent model
    dad_id = SelectField('Father', coerce=int, validators=[InputRequired(message="Please select a father.")])
    # Field for uploading a new main image for the puppy
    image_upload = FileField('Upload New Main Image')


class PuppyAdminView(AdminModelView):
    """Manages the admin interface for Puppy records with Bootstrap 5 templates."""

    # Templates to use for list, create, and edit views
    # Point the view to the Bootstrap 5 templates for a consistent UI.
    list_template = 'admin/puppy/list_bs5.html'
    create_template = 'admin/puppy/create_bs5.html'
    edit_template = 'admin/puppy/edit_bs5.html'
    
    # Define the form and columns to display in the list view.
    column_list = ('name', 'mom', 'dad', 'birth_date', 'status')
    # Form class to use for creating and editing puppies
    form = PuppyForm
    
    # Assign HTML IDs to form fields for easy access by JavaScript.
    form_widget_args = {
        'name': {'id': 'name'},
        'birth_date': {'id': 'birth_date'},
        'status': {'id': 'status'},
        'mom_id': {'id': 'mom_id'},
        'dad_id': {'id': 'dad_id'},
        'image_upload': {'id': 'image_upload'},
    }
    
    def _get_parent_choices(self, role):
        """Fetches a list of active parents (moms or dads) to populate dropdowns."""
        return [(p.id, p.name) for p in Parent.query.filter_by(role=role, is_active=True).order_by(Parent.name).all()]

    def _populate_form_choices(self, form_instance, obj=None):
        """Dynamically populates the 'Mother' and 'Father' dropdowns in the form."""
        # Populate choices for mother and father dropdowns
        form_instance.mom_id.choices = self._get_parent_choices(ParentRole.MOM)
        form_instance.dad_id.choices = self._get_parent_choices(ParentRole.DAD)
        # If editing an existing object, pre-select the current mom and dad
        if obj:
            form_instance.mom_id.data = obj.mom_id
            form_instance.dad_id.data = obj.dad_id
        return form_instance
    
    def create_form(self):
        """Overrides the default form creation to populate parent choices for new puppy."""
        # Call the base class's create_form to get the initial form instance
        form_instance = super().create_form()
        # Populate the parent choices
        return self._populate_form_choices(form_instance)

    def edit_form(self, obj=None):
        """Overrides the default form editing to populate parent choices for existing puppy."""
        # Call the base class's edit_form to get the initial form instance
        form_instance = super().edit_form(obj)
        # Populate the parent choices, passing the existing object for pre-selection
        return self._populate_form_choices(form_instance, obj)

    def on_model_change(self, form, model, is_created):
        """Handles saving relationships and processing image uploads."""
        model.mom = db.session.get(Parent, form.mom_id.data)
        model.dad = db.session.get(Parent, form.dad_id.data)
        
        # Handle image upload if a file is provided
        file = request.files.get('image_upload')
        if file and file.filename:
            # Upload the image to S3 and store the key
            s3_key = upload_image(file, folder='puppies')
            if s3_key:
                model.main_image_s3_key = s3_key