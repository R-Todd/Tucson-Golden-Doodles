# app/routes/admin/views.py

from flask import request, url_for, redirect
from flask_admin import AdminIndexView, expose
from flask_admin.contrib.sqla import ModelView
from flask_login import current_user
from wtforms.fields import SelectField, FileField

from app.models import Parent, ParentRole, PuppyStatus
from app.utils.image_uploader import upload_image

# === Core Admin Views ===
class MyAdminIndexView(AdminIndexView):
    """ Custom admin index view that requires authentication. """
    @expose('/')
    def index(self):
        if not current_user.is_authenticated:
            return redirect(url_for('admin_auth.login'))
        return super(MyAdminIndexView, self).index()

class AdminModelView(ModelView):
    """ Base ModelView that enforces authentication for all model pages. """
    def is_accessible(self):
        return current_user.is_authenticated

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('admin_auth.login', next=request.url))


# === Custom Model Views ===
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

class PuppyAdminView(AdminModelView):
    """ Custom view for the Puppy model with filtered parent dropdowns. """
    form_columns = [
        'name', 'birth_date', 'status', 'mom', 'dad', 'image_upload'
    ]
    form_extra_fields = { 'image_upload': FileField('Upload New Main Image') }
    form_overrides = { 'status': SelectField }
    
    # *** THIS IS THE FIX ***
    # The form_args dictionary MUST contain the query_factory for mom and dad.
    form_args = {
        'mom': {
            'label': 'Mother',
            # This query populates the dropdown only with Parents whose role is MOM.
            'query_factory': lambda: Parent.query.filter_by(role=ParentRole.MOM).all()
        },
        'dad': {
            'label': 'Father',
            # This query populates the dropdown only with Parents whose role is DAD.
            'query_factory': lambda: Parent.query.filter_by(role=ParentRole.DAD).all()
        },
        'status': {
            'label': 'Status',
            'choices': [(s.name, s.value) for s in PuppyStatus],
            'coerce': lambda x: PuppyStatus[x] if isinstance(x, str) else x
        }
    }

    def on_model_change(self, form, model, is_created):
        """ Handle image upload when a Puppy record is saved. """
        file = request.files.get('image_upload')
        if file:
            image_url = upload_image(file, folder='puppies')
            if image_url:
                model.main_image_url = image_url

class HeroSectionAdminView(AdminModelView):
    """ Custom view for the Hero Section with image upload. """
    form_extra_fields = { 'image_upload': FileField('Upload New Image') }
    def on_model_change(self, form, model, is_created):
        file = request.files.get('image_upload')
        if file:
            image_url = upload_image(file, folder='hero')
            if image_url:
                model.image_url = image_url

class AboutSectionAdminView(AdminModelView):
    """ Custom view for the About Section with image upload. """
    form_extra_fields = { 'image_upload': FileField('Upload New Image') }
    def on_model_change(self, form, model, is_created):
        file = request.files.get('image_upload')
        if file:
            image_url = upload_image(file, folder='about')
            if image_url:
                model.image_url = image_url