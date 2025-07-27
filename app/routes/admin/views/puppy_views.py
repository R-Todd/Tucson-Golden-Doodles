# app/routes/admin/views/puppy_views.py

from flask import request
from wtforms.fields import FileField, SelectField
from wtforms.validators import InputRequired
from .base import AdminModelView
from app.models import Parent, ParentRole, PuppyStatus
from app.utils.image_uploader import upload_image

class PuppyAdminView(AdminModelView):
    """ Custom Admin view for managing Puppies. """

    # We can still show the 'mom' and 'dad' relationships in the list view.
    column_list = ('name', 'mom', 'dad', 'birth_date', 'status')
    
    # --- KEY CHANGE 1 ---
    # We only define columns that Flask-Admin can safely scaffold.
    # 'mom' and 'dad' are removed to prevent automatic field generation.
    form_columns = [
        'name',
        'birth_date',
        'status',
        'image_upload' # This is a placeholder that gets replaced by the FileField
    ]

    # --- KEY CHANGE 2 ---
    # We now define our dropdowns with non-conflicting names ('mother' and 'father')
    # and add the required validator since we're creating them from scratch.
    form_extra_fields = {
        'image_upload': FileField('Upload New Main Image'),
        'mother': SelectField(
            'Mother',
            coerce=int,
            validators=[InputRequired(message="Please select a mother.")]
        ),
        'father': SelectField(
            'Father',
            coerce=int,
            validators=[InputRequired(message="Please select a father.")]
        )
    }

    # This part remains simple
    form_overrides = { 'status': SelectField }
    form_args = {
        'status': {
            'label': 'Status',
            'choices': [(s.name, s.value) for s in PuppyStatus],
            'coerce': lambda x: PuppyStatus[x] if isinstance(x, str) else x,
        }
    }

    def _get_parent_choices(self, role):
        """Helper method to get parents for dropdowns."""
        return [(p.id, p.name) for p in Parent.query.filter_by(role=role).order_by(Parent.name).all()]

    def _populate_form_choices(self, form, obj=None):
        """A helper to populate choices for our custom 'mother' and 'father' fields."""
        form.mother.choices = self._get_parent_choices(ParentRole.MOM)
        form.father.choices = self._get_parent_choices(ParentRole.DAD)
        # If we are editing an existing puppy, set the default value for the dropdowns.
        if obj:
            form.mother.data = obj.mom_id
            form.father.data = obj.dad_id
        return form

    def create_form(self):
        """Override to populate choices when creating a new puppy."""
        form = super(PuppyAdminView, self).create_form()
        return self._populate_form_choices(form)

    def edit_form(self, obj=None):
        """Override to populate choices and set defaults when editing a puppy."""
        form = super(PuppyAdminView, self).edit_form(obj)
        form = self._populate_form_choices(form, obj)
        
        # Image preview logic
        if obj and obj.main_image_url:
            if form.image_upload.render_kw is None:
                form.image_upload.render_kw = {}
            form.image_upload.render_kw['data-current-image'] = obj.main_image_url
        return form

    def on_model_change(self, form, model, is_created):
        """
        --- KEY CHANGE 3 ---
        This is crucial. We must now manually map the data from our custom
        'mother' and 'father' form fields back to the model's ID fields.
        """
        model.mom_id = form.mother.data
        model.dad_id = form.father.data
        
        # Image upload logic remains the same
        file = request.files.get('image_upload')
        if file and file.filename:
            image_url = upload_image(file, folder='puppies')
            if image_url:
                model.main_image_url = image_url