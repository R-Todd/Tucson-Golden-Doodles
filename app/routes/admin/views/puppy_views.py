# app/routes/admin/views/puppy_views.py

from flask import request
from wtforms.fields import SelectField, FileField
from .base import AdminModelView
from app.models import Parent, ParentRole, PuppyStatus
from app.utils.image_uploader import upload_image

class PuppyAdminView(AdminModelView):
    """ Custom view for the Puppy model with filtered parent dropdowns. """
    form_columns = [
        'name', 'birth_date', 'status', 'mom', 'dad', 'image_upload'
    ]
    form_extra_fields = { 'image_upload': FileField('Upload New Main Image') }
    form_overrides = { 'status': SelectField }
    
    form_args = {
        'mom': {
            'label': 'Mother',
            'query_factory': lambda: Parent.query.filter_by(role=ParentRole.MOM).all()
        },
        'dad': {
            'label': 'Father',
            'query_factory': lambda: Parent.query.filter_by(role=ParentRole.DAD).all()
        },
        'status': {
            'label': 'Status',
            'choices': [(s.name, s.value) for s in PuppyStatus],
            'coerce': lambda x: PuppyStatus[x] if isinstance(x, str) else x
        }
    }

    def on_model_change(self, form, model, is_created):
        file = request.files.get('image_upload')
        if file:
            image_url = upload_image(file, folder='puppies')
            if image_url:
                model.main_image_url = image_url