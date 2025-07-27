# app/routes/admin/views/parent_views.py

from flask import request
from wtforms import SelectField
from wtforms.fields import FileField
from .base import AdminModelView
from app.models import ParentRole
from app.utils.image_uploader import upload_image

class ParentAdminView(AdminModelView):
    # Use the custom edit template
    edit_template = 'admin/parent_edit.html'

    form_extra_fields = {
        'image_upload': FileField('Upload New Main Image'),
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

    def edit_form(self, obj=None):
        """
        Override the edit_form method to add current image data to the form fields.
        This is the correct place to inject attributes before the template renders.
        """
        form = super(ParentAdminView, self).edit_form(obj)

        if obj: # Ensure we are editing an existing object
            # A mapping of form fields to the corresponding model URL attributes
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
                    # Initialize render_kw if it's None
                    if field.render_kw is None:
                        field.render_kw = {}
                    # Add the data attribute for our JavaScript to use
                    field.render_kw['data-current-image'] = image_url

        return form

    def on_model_change(self, form, model, is_created):
        # ... (this method remains unchanged) ...
        main_file = request.files.get('image_upload')
        if main_file and main_file.filename:
            image_urls = upload_image(main_file, folder='parents', create_responsive_versions=True)
            if image_urls:
                model.main_image_url = image_urls.get('original')
                model.main_image_url_small = image_urls.get('small')
                model.main_image_url_medium = image_urls.get('medium')
                model.main_image_url_large = image_urls.get('large')

        alternate_fields = [
            'alternate_image_upload_1', 'alternate_image_upload_2',
            'alternate_image_upload_3', 'alternate_image_upload_4'
        ]
        alternate_url_columns = [
            'alternate_image_url_1', 'alternate_image_url_2',
            'alternate_image_url_3', 'alternate_image_url_4'
        ]
        for i, field_name in enumerate(alternate_fields):
            alternate_file = request.files.get(field_name)
            if alternate_file and alternate_file.filename:
                alternate_image_url = upload_image(alternate_file, folder='parents_alternates')
                if alternate_image_url:
                    setattr(model, alternate_url_columns[i], alternate_image_url)