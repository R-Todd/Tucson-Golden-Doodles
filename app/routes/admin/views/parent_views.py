# app/routes/admin/views/parent_views.py

from flask import request
from wtforms import SelectField
from wtforms.widgets import Select
from wtforms.fields import FileField
from .base import AdminModelView
from app.models import ParentRole
from app.utils.image_uploader import upload_image

class ParentAdminView(AdminModelView):
    # Use a custom template for the edit page
    edit_template = 'admin/parent_edit.html'
    
    # Define which columns to show in the list view
    column_list = ['name', 'role', 'breed', 'is_active', 'is_guardian']
    
    # --- THIS IS THE CHANGE ---
    # Exclude all image URL fields from the list view for a cleaner look
    column_exclude_list = [
        'main_image_url', 'main_image_url_small', 'main_image_url_medium',
        'main_image_url_large', 'alternate_image_url_1', 'alternate_image_url_2',
        'alternate_image_url_3', 'alternate_image_url_4'
    ]

    # Define fields for the create/edit form
    form_columns = [
        'name', 'role', 'breed', 'birth_date', 'weight_kg', 'height_cm',
        'description', 'is_active', 'is_guardian'
    ]
    
    # Add file upload fields to the form
    form_extra_fields = {
        'image_upload': FileField('Upload/Replace Main Image'),
        'alternate_image_upload_1': FileField('Upload/Replace Alternate Image 1'),
        'alternate_image_upload_2': FileField('Upload/Replace Alternate Image 2'),
        'alternate_image_upload_3': FileField('Upload/Replace Alternate Image 3'),
        'alternate_image_upload_4': FileField('Upload/Replace Alternate Image 4'),
    }
    
    form_overrides = { 'role': SelectField }

    form_args = {
        'role': {
            'label': 'Role',
            'choices': [(role.name, role.value) for role in ParentRole],
            'coerce': lambda x: ParentRole[x] if isinstance(x, str) else x,
            'widget': Select()
        }
    }

    def edit_form(self, obj=None):
        form = super(ParentAdminView, self).edit_form(obj)
        if obj:
            image_fields = {
                'image_upload': obj.main_image_url,
                'alternate_image_upload_1': obj.alternate_image_url_1,
                'alternate_image_upload_2': obj.alternate_image_url_2,
                'alternate_image_upload_3': obj.alternate_image_url_3,
                'alternate_image_upload_4': obj.alternate_image_url_4,
            }
            for field_name, image_url in image_fields.items():
                if hasattr(form, field_name) and image_url:
                    field = getattr(form, field_name)
                    if field.render_kw is None:
                        field.render_kw = {}
                    field.render_kw['data-current-image'] = image_url
        return form

    def on_model_change(self, form, model, is_created):
        main_file = request.files.get('image_upload')
        if main_file and main_file.filename:
            image_urls = upload_image(main_file, folder='parents', create_responsive_versions=True)
            if image_urls:
                model.main_image_url = image_urls.get('original')
                model.main_image_url_small = image_urls.get('small')
                model.main_image_url_medium = image_urls.get('medium')
                model.main_image_url_large = image_urls.get('large')

        alt_fields = ['alternate_image_upload_1', 'alternate_image_upload_2', 'alternate_image_upload_3', 'alternate_image_upload_4']
        alt_cols = ['alternate_image_url_1', 'alternate_image_url_2', 'alternate_image_url_3', 'alternate_image_url_4']

        for i, field_name in enumerate(alt_fields):
            file = request.files.get(field_name)
            if file and file.filename:
                url = upload_image(file, folder='parents_alternates')
                if url:
                    setattr(model, alt_cols[i], url)