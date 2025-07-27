# app/routes/admin/views/puppy_views.py

from flask import request
from wtforms.fields import FileField, SelectField
from flask_admin.contrib.sqla.fields import QuerySelectField # Import this
from .base import AdminModelView
from app.models import Parent, ParentRole, PuppyStatus
from app.utils.image_uploader import upload_image

class PuppyAdminView(AdminModelView):
    """ Custom Admin view for managing Puppies. """
    
    # Columns to display in the create/edit forms.
    form_columns = [
        'name',
        'birth_date',
        'status',
        'mom',
        'dad',
        'image_upload'  # Custom field for upload
    ]

    # Add the non-model field for file uploads.
    form_extra_fields = {
        'image_upload': FileField('Upload New Main Image')
    }

    # Explicitly override the fields to ensure standard widgets are used,
    # preventing the Select2 widget compatibility issue.
    form_overrides = {
        'mom': QuerySelectField,
        'dad': QuerySelectField,
        'status': SelectField
    }
    
    # Configure the arguments for the overridden fields.
    form_args = {
        'mom': {
            'label': 'Mother',
            'query_factory': lambda: Parent.query.filter_by(role=ParentRole.MOM).all(),
            'allow_blank': False,
        },
        'dad': {
            'label': 'Father',
            'query_factory': lambda: Parent.query.filter_by(role=ParentRole.DAD).all(),
            'allow_blank': False,
        },
        'status': {
            'label': 'Status',
            'choices': [(s.name, s.value) for s in PuppyStatus],
            # Coerce the form string back into a PuppyStatus Enum object
            'coerce': lambda x: PuppyStatus[x] if isinstance(x, str) else x
        }
    }

    # This method adds a preview of the current image to the edit form.
    def edit_form(self, obj=None):
        form = super(PuppyAdminView, self).edit_form(obj)
        if obj and obj.main_image_url:
            if form.image_upload.render_kw is None:
                form.image_upload.render_kw = {}
            # Pass the image URL to the template via the field's render_kw
            form.image_upload.render_kw['data-current-image'] = obj.main_image_url
        return form

    # This method handles the file upload logic when the form is submitted.
    def on_model_change(self, form, model, is_created):
        file = request.files.get('image_upload')
        if file and file.filename:
            # Upload the image and save the URL to the model.
            image_url = upload_image(file, folder='puppies')
            if image_url:
                model.main_image_url = image_url