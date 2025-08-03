# app/routes/admin/views/parent_views.py

from flask import request
from .base import AdminModelView
from app.utils.image_uploader import upload_image
from ..forms import ParentForm 

class ParentAdminView(AdminModelView):
    edit_template = 'admin/parent_edit.html'
    create_template = 'admin/parent_edit.html'
    column_list = ['name', 'role', 'breed', 'is_active', 'is_guardian']
    form = ParentForm

    def edit_form(self, obj=None):
        form = super(ParentAdminView, self).edit_form(obj)
        
        # This logic adds the 'data-current-image' attribute for the previews
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

    # --- THIS METHOD IS NOW RESTORED ---
    def on_model_change(self, form, model, is_created):
        """Handle image uploads when a parent record is saved."""
        main_file = request.files.get('image_upload')
        if main_file and main_file.filename:
            image_urls = upload_image(main_file, folder='parents', create_responsive_versions=True)
            if image_urls:
                model.main_image_url = image_urls.get('original')
                model.main_image_url_small = image_urls.get('small')
                model.main_image_url_medium = image_urls.get('medium')
                model.main_image_url_large = image_urls.get('large')

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
                url = upload_image(file, folder='parents_alternates')
                if url:
                    setattr(model, alt_model_attrs[i], url)