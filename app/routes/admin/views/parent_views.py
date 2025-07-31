# app/routes/admin/views/parent_views.py

from flask import request
from .base import AdminModelView
from app.utils.image_uploader import upload_image
from ..forms import ParentForm # Import the new ParentForm

class ParentAdminView(AdminModelView):
    # Use the custom template for both editing and creating
    edit_template = 'admin/parent_edit.html'
    create_template = 'admin/parent_edit.html'

    # Define the columns to show in the list view
    column_list = ['name', 'role', 'breed', 'is_active', 'is_guardian']

    # Assign the custom form to the view
    form = ParentForm

    def on_model_change(self, form, model, is_created):
        """Handle image uploads when a parent record is saved."""
        # --- Main Image ---
        main_file = request.files.get('image_upload')
        if main_file and main_file.filename:
            # This function creates and uploads multiple sizes
            image_urls = upload_image(main_file, folder='parents', create_responsive_versions=True)
            if image_urls:
                model.main_image_url = image_urls.get('original')
                model.main_image_url_small = image_urls.get('small')
                model.main_image_url_medium = image_urls.get('medium')
                model.main_image_url_large = image_urls.get('large')

        # --- Alternate Images ---
        alt_fields = [
            'alternate_image_upload_1', 'alternate_image_upload_2',
            'alternate_image_upload_3', 'alternate_image_upload_4'
        ]
        alt_model_attrs = [
            'alternate_image_url_1', 'alternate_image_url_2',
            'alternate_image_url_3', 'alternate_image_url_4'
        ]

        for i, field_name in enumerate(alt_fields):
            file = request.files.get(field_name)
            if file and file.filename:
                # Alternate images don't need responsive versions
                url = upload_image(file, folder='parents_alternates')
                if url:
                    # e.g., setattr(model, 'alternate_image_url_1', url)
                    setattr(model, alt_model_attrs[i], url)