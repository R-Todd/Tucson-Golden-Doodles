# app/routes/admin/views/puppy_views.py
from flask_admin.model import InlineFormAdmin
from .base import AdminModelView
from app.models import Puppy, Litter, db

class PuppyInlineModelForm(InlineFormAdmin):
    """Allows adding puppies directly on the Litter page."""
    form_columns = ('id', 'name', 'gender', 'status', 'main_image_s3_key')

class LitterAdminView(AdminModelView):
    """New view for managing litters and their puppies."""
    column_list = ('birth_date', 'mom', 'dad', 'breed', 'expected_size')
    form_columns = ('birth_date', 'mom', 'dad', 'breed', 'expected_size')
    inline_models = (PuppyInlineModelForm(Puppy),)

class PuppyAdminView(AdminModelView):
    """Updated individual puppy view."""
    column_list = ('name', 'litter', 'status')
    form_columns = ('name', 'litter', 'status', 'gender', 'coat_color', 'main_image_s3_key')