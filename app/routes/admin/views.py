# app/routes/admin/views.py

from flask import request, url_for, redirect
from flask_admin import AdminIndexView, expose
from flask_admin.contrib.sqla import ModelView
from flask_login import current_user
from wtforms.fields import SelectField, FileField

# Make sure Parent and ParentRole are imported
from app.models import Parent, ParentRole, PuppyStatus
from app.utils.image_uploader import upload_image

# NEW: MyAdminIndexView is now in this file where it belongs
class MyAdminIndexView(AdminIndexView):
    """
    Custom Admin index view that handles authentication.
    It redirects unauthenticated users to the login page.
    """
    @expose('/')
    def index(self):
        # This check ensures that only logged-in users can see the admin dashboard
        if not current_user.is_authenticated:
            # Redirect to the login view within the 'admin_auth' blueprint
            return redirect(url_for('admin_auth.login'))
        # If authenticated, render the default admin index page
        return super(MyAdminIndexView, self).index()

# Base view with authentication
class AdminModelView(ModelView):
    """
    Base ModelView that enforces authentication for all admin pages.
    """
    def is_accessible(self):
        # This method from Flask-Login checks if the current user is logged in
        return current_user.is_authenticated

    def inaccessible_callback(self, name, **kwargs):
        # If is_accessible() returns False, this function is called.
        # It redirects the user to the login page.
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

# THIS IS THE CORRECTED VIEW FOR YOUR PUPPY MODEL
class PuppyAdminView(AdminModelView):
    # Explicitly define the columns to show in the form
    form_columns = [
        'name',
        'birth_date',
        'status',
        'mom',  # Use the relationship name from the Puppy model
        'dad',  # Use the relationship name from the Puppy model
        'image_upload' # The extra field for file uploads
    ]

    form_extra_fields = {
        'image_upload': FileField('Upload New Main Image')
    }

    form_overrides = {
        'status': SelectField
    }

    # Add arguments to configure the dropdowns correctly
    form_args = {
        'status': {
            'label': 'Status',
            'choices': [(status.name, status.value) for status in PuppyStatus],
            'coerce': lambda x: PuppyStatus[x] if isinstance(x, str) else x
        },
        'mom': {
            'label': 'Mom',
            # This query ensures only parents with the 'MOM' role appear
            'query_factory': lambda: Parent.query.filter_by(role=ParentRole.MOM).all()
        },
        'dad': {
            'label': 'Dad',
            # This query ensures only parents with the 'DAD' role appear
            'query_factory': lambda: Parent.query.filter_by(role=ParentRole.DAD).all()
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