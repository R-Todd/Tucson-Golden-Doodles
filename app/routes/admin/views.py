from flask import request, url_for, redirect
from flask_admin.contrib.sqla import ModelView
from flask_login import current_user
from wtforms.fields import SelectField, FileField

from app.models import ParentRole, PuppyStatus
from app.utils.image_uploader import upload_image

# Base view with authentication
class AdminModelView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated

    def inaccessible_callback(self, name, **kwargs):
        # Redirect to login page if user doesn't have access
        return redirect(url_for('admin_auth.login', next=request.url))

# Custom view for the Parent model
class ParentAdminView(AdminModelView):
    form_extra_fields = {
        'image_upload': FileField('Upload New Main Image')
    }
    form_overrides = {
        'role': SelectField
    }
    form_args = {
        'role': {
            'label': 'Role',
            'choices': [(role.name, role.value) for role in ParentRole],
            'coerce': lambda x: ParentRole[x] if isinstance(x, str) else x
        }
    }
    def on_model_change(self, form, model, is_created):
        file = request.files.get('image_upload')
        if file:
            image_url = upload_image(file, folder='parents')
            if image_url:
                model.main_image_url = image_url

# Custom view for the Puppy model
class PuppyAdminView(AdminModelView):
    form_extra_fields = {
        'image_upload': FileField('Upload New Main Image')
    }
    form_overrides = {
        'status': SelectField
    }
    form_args = {
        'status': {
            'label': 'Status',
            'choices': [(status.name, status.value) for status in PuppyStatus],
            'coerce': lambda x: PuppyStatus[x] if isinstance(x, str) else x
        }
    }
    def on_model_change(self, form, model, is_created):
        file = request.files.get('image_upload')
        if file:
            image_url = upload_image(file, folder='puppies')
            if image_url:
                model.main_image_url = image_url

# Custom view for the Hero Section model
class HeroSectionAdminView(AdminModelView):
    form_extra_fields = {
        'image_upload': FileField('Upload New Image')
    }

    def on_model_change(self, form, model, is_created):
        file = request.files.get('image_upload')
        if file:
            image_url = upload_image(file, folder='hero')
            if image_url:
                model.image_url = image_url

# Custom view for the About Section model
class AboutSectionAdminView(AdminModelView):
    form_extra_fields = {
        'image_upload': FileField('Upload New Image')
    }

    def on_model_change(self, form, model, is_created):
        file = request.files.get('image_upload')
        if file:
            image_url = upload_image(file, folder='about')
            if image_url:
                model.image_url = image_url