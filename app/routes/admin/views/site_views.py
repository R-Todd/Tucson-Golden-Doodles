# app/routes/admin/views/site_views.py

from flask import request
from wtforms.fields import FileField
from .base import AdminModelView
from app.utils.image_uploader import upload_image
from ..forms import AnnouncementBannerForm # CORRECTED IMPORT
from app.models import AnnouncementBanner

class HeroSectionAdminView(AdminModelView):
    """ Custom view for the Hero Section with image upload. """
    
    column_list = ('main_title', 'subtitle', 'description')
    form_columns = [
        'main_title', 'subtitle', 'description', 'scroll_text_main',
        'scroll_text_secondary', 'image_upload'
    ]
    form_extra_fields = {
        'image_upload': FileField('Upload New Background Image (Recommended: 1920x1080px)')
    }

    def edit_form(self, obj=None):
        form = super(HeroSectionAdminView, self).edit_form(obj)
        if obj and obj.image_url:
            if form.image_upload.render_kw is None:
                form.image_upload.render_kw = {}
            form.image_upload.render_kw['data-current-image'] = obj.image_url
        return form

    def on_model_change(self, form, model, is_created):
        file = request.files.get('image_upload')
        if file and file.filename:
            image_urls = upload_image(file, folder='hero', create_responsive_versions=True)
            if image_urls:
                model.image_url = image_urls.get('original')
                model.image_url_small = image_urls.get('small')
                model.image_url_medium = image_urls.get('medium')
                model.image_url_large = image_urls.get('large')


class AboutSectionAdminView(AdminModelView):
    """ Custom view for the About Section with image upload. """
    form_extra_fields = { 'image_upload': FileField('Upload New Image') }

    def edit_form(self, obj=None):
        form = super(AboutSectionAdminView, self).edit_form(obj)
        if obj and obj.image_url:
            if form.image_upload.render_kw is None:
                form.image_upload.render_kw = {}
            form.image_upload.render_kw['data-current-image'] = obj.image_url
        return form

    def on_model_change(self, form, model, is_created):
        file = request.files.get('image_upload')
        if file and file.filename:
            image_urls = upload_image(file, folder='about', create_responsive_versions=True)
            if image_urls:
                model.image_url = image_urls.get('original')
                model.image_url_small = image_urls.get('small')
                model.image_url_medium = image_urls.get('medium')
                model.image_url_large = image_urls.get('large')

class AnnouncementBannerAdminView(AdminModelView):
    """Custom Admin View for the Announcement Banner."""
    form = AnnouncementBannerForm
    
    column_list = ('is_active', 'main_text', 'featured_puppy')

    def on_model_change(self, form, model, is_created):
        """Saves the relationship between the banner and the selected puppy."""
        selected_puppy = form.featured_puppy.data
        if selected_puppy:
            model.featured_puppy_id = selected_puppy.id
        else:
            model.featured_puppy_id = None