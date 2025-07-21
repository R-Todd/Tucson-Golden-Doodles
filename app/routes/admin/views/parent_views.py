# app/routes/admin/views/parent_views.py

from flask import request
from wtforms.fields import SelectField, FileField
from .base import AdminModelView
from app.models import ParentRole
from app.utils.image_uploader import upload_image

class ParentAdminView(AdminModelView):
    """ Custom view for the Parent model. """
    form_extra_fields = { 'image_upload': FileField('Upload New Main Image') }
    form_overrides = { 'role': SelectField }
    form_args = {
        'role': {
            'label': 'Role',
            'choices': [(role.name, role.value) for role in ParentRole],
            'coerce': lambda x: ParentRole[x] if isinstance(x, str) else x
        }
    }

    def on_model_change(self, form, model, is_created):
        """ Handle image upload when a Parent record is saved. """
        file = request.files.get('image_upload')
        if file:
            image_url = upload_image(file, folder='parents')
            if image_url:
                model.main_image_url = image_url