# app/routes/admin/views/parent_views.py

from flask import request
from .base import AdminModelView
from app.utils.image_uploader import upload_image
from app.routes.admin.forms.parent_forms import ParentForm 

class ParentAdminView(AdminModelView):
    """Custom Admin View for Parents with Bootstrap 5 templates and live preview."""

    # Template and Form Configuration
    list_template = 'admin/parent/list_bs5.html'
    create_template = 'admin/parent/create_bs5.html'
    edit_template = 'admin/parent/edit_bs5.html'
    form = ParentForm
    
    column_list = ['name', 'role', 'breed', 'is_active', 'is_guardian']

    form_widget_args = {
        'name': { 'id': 'name' },
        'breed': { 'id': 'breed' },
        'weight_kg': { 'id': 'weight_kg' },
        'description': { 'id': 'description', 'rows': 10 },
        'image_upload': {'id': 'image_upload'},
        'alternate_image_upload_1': {'id': 'alternate_image_upload_1'},
        'alternate_image_upload_2': {'id': 'alternate_image_upload_2'},
        'alternate_image_upload_3': {'id': 'alternate_image_upload_3'},
        'alternate_image_upload_4': {'id': 'alternate_image_upload_4'},
    }

    def on_model_change(self, form, model, is_created):
        # Image upload logic remains the same
        main_file = request.files.get('image_upload')
        if main_file and main_file.filename:
            s3_keys = upload_image(main_file, folder='parents', create_responsive_versions=True)
            if s3_keys:
                model.main_image_s3_key = s3_keys.get('original')
                model.main_image_s3_key_large = s3_keys.get('large')

        alt_fields = [f'alternate_image_upload_{i}' for i in range(1, 5)]
        alt_model_attrs = [f'alternate_image_s3_key_{i}' for i in range(1, 5)]

        for i, field_name in enumerate(alt_fields):
            file = request.files.get(field_name)
            if file and file.filename:
                key = upload_image(file, folder='parents_alternates')
                if key:
                    setattr(model, alt_model_attrs[i], key)