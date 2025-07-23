# app/routes/admin/views/site_views.py

from flask import request
from wtforms.fields import FileField
from .base import AdminModelView
from app.utils.image_uploader import upload_image

class HeroSectionAdminView(AdminModelView):
    """ Custom view for the Hero Section with image upload. """
    form_extra_fields = { 'image_upload': FileField('Upload New Image') }
    def on_model_change(self, form, model, is_created):
        # --- MODIFIED SECTION ---
        file = request.files.get('image_upload')
        if file and file.filename:
            # Create responsive versions for the hero image
            image_urls = upload_image(file, folder='hero', create_responsive_versions=True)
            if image_urls:
                # Save the new URLs to the model
                model.image_url = image_urls.get('original') # Fallback
                model.image_url_small = image_urls.get('small')
                model.image_url_medium = image_urls.get('medium')
                model.image_url_large = image_urls.get('large')

class AboutSectionAdminView(AdminModelView):
    """ Custom view for the About Section with image upload. """
    form_extra_fields = { 'image_upload': FileField('Upload New Image') }
    def on_model_change(self, form, model, is_created):
        # --- MODIFIED SECTION ---
        file = request.files.get('image_upload')
        if file and file.filename:
            # Create responsive versions for the about section image
            image_urls = upload_image(file, folder='about', create_responsive_versions=True)
            if image_urls:
                # Save the new URLs to the model
                model.image_url = image_urls.get('original') # Fallback
                model.image_url_small = image_urls.get('small')
                model.image_url_medium = image_urls.get('medium')
                model.image_url_large = image_urls.get('large')