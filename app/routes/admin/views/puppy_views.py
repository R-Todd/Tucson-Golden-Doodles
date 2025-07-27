# app/routes/admin/views/puppy_views.py

from flask import request
from wtforms.fields import FileField, SelectField
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
        'mom': SelectField,
        'dad': SelectField,
        'status': SelectField
    }
    
    form_args = {
        'status': {
            'label': 'Status',
            'choices': [(s.name, s.value) for s in PuppyStatus],
            'coerce': lambda x: PuppyStatus[x] if isinstance(x, str) else x,
        },
        'mom': {
            'label': 'Mother',
            'coerce': int,
            # --- THIS LINE IS REMOVED ---
            # 'allow_blank': False 
        },
        'dad': {
            'label': 'Father',
            'coerce': int,
            # --- THIS LINE IS REMOVED ---
            # 'allow_blank': False
        }
    }

    def _get_parent_choices(self, role):
        """Helper method to get parents for dropdowns."""
        return [(p.id, p.name) for p in Parent.query.filter_by(role=role).order_by(Parent.name).all()]

    def create_form(self):
        """Dynamically set choices for mom and dad dropdowns on the create form."""
        form = super(PuppyAdminView, self).create_form()
        form.mom.choices = self._get_parent_choices(ParentRole.MOM)
        form.dad.choices = self._get_parent_choices(ParentRole.DAD)
        return form

    def edit_form(self, obj=None):
        """Dynamically set choices for mom and dad dropdowns on the edit form."""
        form = super(PuppyAdminView, self).edit_form(obj)
        form.mom.choices = self._get_parent_choices(ParentRole.MOM)
        form.dad.choices = self._get_parent_choices(ParentRole.DAD)
        
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