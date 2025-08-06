# app/routes/admin/views/parent_views.py

from flask import request
from .base import AdminModelView
from app.utils.image_uploader import upload_image, generate_presigned_url
from ..forms import ParentForm 

class ParentAdminView(AdminModelView):
    edit_template = 'admin/parent_edit.html'
    create_template = 'admin/parent_edit.html'
    column_list = ['name', 'role', 'breed', 'is_active', 'is_guardian']
    form = ParentForm

    # --- THIS IS THE CORRECTED SECTION ---
    # We've added the 'weight_kg' field here so the JavaScript can find it.
    form_widget_args = {
        'name': { 'id': 'name' },
        'breed': { 'id': 'breed' },
        'weight_kg': { 'id': 'weight_kg' }, # <-- ADD THIS LINE
        'description': { 'id': 'description', 'rows': 10 }
    }

    def edit_form(self, obj=None):
        form = super(ParentAdminView, self).edit_form(obj)
        return form

    def on_model_change(self, form, model, is_created):
        main_file = request.files.get('image_upload')
        if main_file and main_file.filename:
            s3_keys = upload_image(main_file, folder='parents', create_responsive_versions=True)
            if s3_keys:
                model.main_image_s3_key = s3_keys.get('original')
                model.main_image_s3_key_small = s3_keys.get('small')
                model.main_image_s3_key_medium = s3_keys.get('medium')
                model.main_image_s3_key_large = s3_keys.get('large')

        alt_fields = [
            'alternate_image_upload_1', 'alternate_image_upload_2',
            'alternate_image_upload_3', 'alternate_image_upload_4'
        ]
        alt_model_attrs = [
            'alternate_image_s3_key_1', 'alternate_image_s3_key_2',
            'alternate_image_s3_key_3', 'alternate_image_s3_key_4'
        ]

        for i, field_name in enumerate(alt_fields):
            file = request.files.get(field_name)
            if file and file.filename:
                key = upload_image(file, folder='parents_alternates')
                if key:
                    setattr(model, alt_model_attrs[i], key)