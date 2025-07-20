# app/routes/admin/views.py

from flask import request, url_for, redirect
from flask_admin import AdminIndexView, expose
from flask_admin.contrib.sqla import ModelView
from flask_login import current_user
from wtforms.fields import SelectField, FileField

# Make sure Parent, ParentRole, and PuppyStatus are imported
from app.models import Parent, ParentRole, PuppyStatus
from app.utils.image_uploader import upload_image

class MyAdminIndexView(AdminIndexView):
    @expose('/')
    def index(self):
        if not current_user.is_authenticated:
            return redirect(url_for('admin_auth.login'))
        return super(MyAdminIndexView, self).index()

class AdminModelView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated
    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('admin_auth.login', next=request.url))

class ParentAdminView(AdminModelView):
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
        file = request.files.get('image_upload')
        if file:
            image_url = upload_image(file, folder='parents')
            if image_url:
                model.main_image_url = image_url

# THIS IS THE FINAL FIX: The PuppyAdminView is now simplified.
class PuppyAdminView(AdminModelView):
    # Explicitly list the form columns. Flask-Admin will now automatically
    # create the correct dropdowns for 'mom' and 'dad'.
    form_columns = [
        'name',
        'birth_date',
        'status',
        'mom',
        'dad',
        'image_upload'
    ]

    form_extra_fields = { 'image_upload': FileField('Upload New Main Image') }
    form_overrides = { 'status': SelectField }
    
    # We only need to configure the 'status' dropdown. The 'mom' and 'dad'
    # dropdowns will now work automatically.
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

class HeroSectionAdminView(AdminModelView):
    form_extra_fields = { 'image_upload': FileField('Upload New Image') }
    def on_model_change(self, form, model, is_created):
        file = request.files.get('image_upload')
        if file:
            image_url = upload_image(file, folder='hero')
            if image_url:
                model.image_url = image_url

class AboutSectionAdminView(AdminModelView):
    form_extra_fields = { 'image_upload': FileField('Upload New Image') }
    def on_model_change(self, form, model, is_created):
        file = request.files.get('image_upload')
        if file:
            image_url = upload_image(file, folder='about')
            if image_url:
                model.image_url = image_url