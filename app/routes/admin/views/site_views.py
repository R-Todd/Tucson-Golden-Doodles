# app/routes/admin/views/site_views.py

from flask import request
from wtforms.fields import FileField
from .base import AdminModelView
from app.utils.image_uploader import upload_image

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