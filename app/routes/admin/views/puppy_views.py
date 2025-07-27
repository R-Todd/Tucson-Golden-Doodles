# app/routes/admin/views/puppy_views.py

from flask import request
from wtforms.fields import FileField, SelectField
from wtforms.widgets import Select # <-- Import the basic widget
from flask_admin.contrib.sqla.fields import QuerySelectField
from .base import AdminModelView
from app.models import Parent, ParentRole, PuppyStatus
from app.utils.image_uploader import upload_image

class PuppyAdminView(AdminModelView):
    """ Custom Admin view for managing Puppies. """

    column_list = ('name', 'mom', 'dad', 'birth_date', 'status')
    
    form_columns = [
        'name',
        'birth_date',
        'status',
        'mom',
        'dad',
        'image_upload'
    ]

    form_extra_fields = {
        'image_upload': FileField('Upload New Main Image')
    }

    form_overrides = {
        'mom': QuerySelectField,
        'dad': QuerySelectField,
        'status': SelectField
    }
    
    # This is the crucial part of the fix
    form_args = {
        'mom': {
            'label': 'Mother',
            'query_factory': lambda: Parent.query.filter_by(role=ParentRole.MOM).all(),
            'allow_blank': False,
            'widget': Select() # Force the use of the standard widget
        },
        'dad': {
            'label': 'Father',
            'query_factory': lambda: Parent.query.filter_by(role=ParentRole.DAD).all(),
            'allow_blank': False,
            'widget': Select() # Force the use of the standard widget
        },
        'status': {
            'label': 'Status',
            'choices': [(s.name, s.value) for s in PuppyStatus],
            'coerce': lambda x: PuppyStatus[x] if isinstance(x, str) else x,
            'widget': Select() # Force the use of the standard widget
        }
    }

    def edit_form(self, obj=None):
        form = super(PuppyAdminView, self).edit_form(obj)
        if obj and obj.main_image_url:
            if form.image_upload.render_kw is None:
                form.image_upload.render_kw = {}
            form.image_upload.render_kw['data-current-image'] = obj.main_image_url
        return form

    def on_model_change(self, form, model, is_created):
        file = request.files.get('image_upload')
        if file and file.filename:
            image_url = upload_image(file, folder='puppies')
            if image_url:
                model.main_image_url = image_url