# app/routes/admin/views/parent_views.py

from flask import request
from wtforms import SelectField
from wtforms.fields import FileField # Ensure FileField is imported
# No longer need InlineFormAdmin here as we're using fixed fields
# from flask_admin.model.form import InlineFormAdmin 
from .base import AdminModelView
from app.models import ParentRole # No longer need ParentImage here as it's not inline
from app.utils.image_uploader import upload_image

# Remove ParentImageInlineForm definition as it's no longer used for fixed slots

class ParentAdminView(AdminModelView):
    form_extra_fields = {
        'image_upload': FileField('Upload New Main Image'),
        # New: Add FileFields for 4 alternate images
        'alternate_image_upload_1': FileField('Upload Alternate Image 1'),
        'alternate_image_upload_2': FileField('Upload Alternate Image 2'),
        'alternate_image_upload_3': FileField('Upload Alternate Image 3'),
        'alternate_image_upload_4': FileField('Upload Alternate Image 4'),
    }
    form_overrides = { 'role': SelectField }
    form_args = {
        'role': {
            'label': 'Role',
            'choices': [(role.name, role.value) for role in ParentRole],
            'coerce': lambda x: ParentRole[x] if isinstance(x, str) else x
        }
    }

    # Remove inline_models configuration
    # inline_models = (ParentImageInlineForm(ParentImage),)

    def on_model_change(self, form, model, is_created):
        """
        Handles image uploads for the main parent image and the 4 alternate images.
        """
        # Handle the main parent image upload (existing logic)
        main_file = request.files.get('image_upload')
        if main_file and main_file.filename:
            main_image_url = upload_image(main_file, folder='parents')
            if main_image_url:
                model.main_image_url = main_image_url

        # New: Handle uploads for the 4 alternate images
        alternate_fields = [
            'alternate_image_upload_1',
            'alternate_image_upload_2',
            'alternate_image_upload_3',
            'alternate_image_upload_4'
        ]
        alternate_url_columns = [
            'alternate_image_url_1',
            'alternate_image_url_2',
            'alternate_image_url_3',
            'alternate_image_url_4'
        ]

        for i, field_name in enumerate(alternate_fields):
            alternate_file = request.files.get(field_name)
            if alternate_file and alternate_file.filename:
                alternate_image_url = upload_image(alternate_file, folder='parents_alternates') # New folder for alternate images
                if alternate_image_url:
                    setattr(model, alternate_url_columns[i], alternate_image_url)