# app/routes/admin/views/parent_views.py

from flask import request
from wtforms import SelectField
from wtforms.fields import FileField # Ensure FileField is imported
from .base import AdminModelView
from app.models import ParentRole
from app.utils.image_uploader import upload_image

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

    def on_model_change(self, form, model, is_created):
        """
        Handles image uploads for the main parent image and the 4 alternate images.
        """
        # --- MODIFIED SECTION ---
        # Handle the main parent image upload with responsive versions
        main_file = request.files.get('image_upload')
        if main_file and main_file.filename:
            # Call the uploader to create multiple sizes
            image_urls = upload_image(main_file, folder='parents', create_responsive_versions=True)
            if image_urls:
                # Save the new URLs to the corresponding model fields
                model.main_image_url = image_urls.get('original') # Fallback
                model.main_image_url_small = image_urls.get('small')
                model.main_image_url_medium = image_urls.get('medium')
                model.main_image_url_large = image_urls.get('large')

        # --- UNCHANGED SECTION ---
        # Handle uploads for the 4 alternate images as single files
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
                # This call does NOT create responsive versions, so it works as before
                alternate_image_url = upload_image(alternate_file, folder='parents_alternates')
                if alternate_image_url:
                    setattr(model, alternate_url_columns[i], alternate_image_url)