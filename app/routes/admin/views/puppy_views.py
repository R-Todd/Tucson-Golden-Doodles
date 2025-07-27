# app/routes/admin/views/puppy_views.py

from flask import request
# Import FlaskForm from flask_wtf
from flask_wtf import FlaskForm #
from wtforms.fields import FileField, SelectField, DateField, StringField
from wtforms.validators import InputRequired, DataRequired
from .base import AdminModelView
from app.models import Parent, ParentRole, PuppyStatus
from app.utils.image_uploader import upload_image

# --- KEY CHANGE 1: Define a custom form ---
# Inherit from FlaskForm for proper WTForms/Flask-Admin integration.
class PuppyForm(FlaskForm): #
    # Removed custom __init__ method here
    
    name = StringField('Name', validators=[DataRequired()])
    birth_date = DateField('Birth Date', validators=[DataRequired()])
    status = SelectField(
        'Status',
        choices=[(s.name, s.value) for s in PuppyStatus],
        coerce=lambda x: PuppyStatus[x] if isinstance(x, str) else x,
        validators=[DataRequired()]
    )
    # Define mom and dad fields with the correct names from the start
    mom = SelectField(
        'Mother',
        coerce=int,
        validators=[InputRequired(message="Please select a mother.")]
    )
    dad = SelectField(
        'Father',
        coerce=int,
        validators=[InputRequired(message="Please select a father.")]
    )
    image_upload = FileField('Upload New Main Image')


class PuppyAdminView(AdminModelView):
    """ Custom Admin view for managing Puppies using a custom form. """

    column_list = ('name', 'mom', 'dad', 'birth_date', 'status')
    
    # --- KEY CHANGE 2: Tell Flask-Admin to use our custom form ---
    form = PuppyForm
    
    # We no longer need: form_columns, form_excluded_columns, form_extra_fields,
    # form_overrides, or form_args. They are all handled by the PuppyForm class.

    def _get_parent_choices(self, role):
        """Helper method to get parents for dropdowns."""
        return [(p.id, p.name) for p in Parent.query.filter_by(role=role).order_by(Parent.name).all()]

    def _populate_form_choices(self, form_instance, obj=None):
        """A helper to populate choices for our 'mom' and 'dad' fields."""
        # The form is now guaranteed to have these fields.
        form_instance.mom.choices = self._get_parent_choices(ParentRole.MOM)
        form_instance.dad.choices = self._get_parent_choices(ParentRole.DAD)
        if obj:
            form_instance.mom.data = obj.mom_id
            form_instance.dad.data = obj.dad_id
        return form_instance

    def create_form(self):
        """Override to populate choices when creating a new puppy."""
        form_instance = super().create_form()
        return self._populate_form_choices(form_instance)

    def edit_form(self, obj=None):
        """Override to populate choices and set defaults when editing a puppy."""
        form_instance = super().edit_form(obj)
        form_instance = self._populate_form_choices(form_instance, obj)
        
        if obj and obj.main_image_url:
            if form_instance.image_upload.render_kw is None:
                form_instance.image_upload.render_kw = {}
            form_instance.image_upload.render_kw['data-current-image'] = obj.main_image_url
        return form_instance

    def on_model_change(self, form, model, is_created):
        """
        Map the data from our custom form fields back to the model's ID fields.
        """
        model.mom_id = form.mom.data
        model.dad_id = form.dad.data
        
        file = request.files.get('image_upload')
        if file and file.filename:
            image_url = upload_image(file, folder='puppies')
            if image_url:
                model.main_image_url = image_url