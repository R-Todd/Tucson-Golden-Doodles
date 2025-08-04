# app/routes/admin/views/site_views.py

from flask import request
from wtforms.fields import FileField
from .base import AdminModelView
from app.utils.image_uploader import upload_image, generate_presigned_url
from ..forms import AnnouncementBannerForm
from app.models import AnnouncementBanner

class HeroSectionAdminView(AdminModelView):
    """ Custom view for the Hero Section with image upload. """
    
    edit_template = 'admin/hero_section_edit.html'
    column_list = ('main_title', 'subtitle', 'description')
    form_columns = [
        'main_title', 'subtitle', 'description', 'scroll_text_main',
        'scroll_text_secondary', 'image_upload'
    ]
    form_extra_fields = {
        'image_upload': FileField('Upload New Background Image (Recommended: 1920x1080px)')
    }

    
    # Assign explicit IDs to each form field so the JavaScript can find them.
    # The 'id' directly corresponds to the ID the JavaScript will look for.
    form_widget_args = {
        'main_title': {
            'id': 'main_title'
        },
        'subtitle': {
            'id': 'subtitle'
        },
        'description': {
            'id': 'description'
        },
        'scroll_text_main': {
            'id': 'scroll_text_main'
        },
        'scroll_text_secondary': {
            'id': 'scroll_text_secondary'
        },
    }

    def edit_form(self, obj=None):
        form = super(HeroSectionAdminView, self).edit_form(obj)
        if obj and obj.image_s3_key:
            if form.image_upload.render_kw is None:
                form.image_upload.render_kw = {}
            form.image_upload.render_kw['data-current-image'] = generate_presigned_url(obj.image_s3_key)
        return form

    def on_model_change(self, form, model, is_created):
        file = request.files.get('image_upload')
        if file and file.filename:
            s3_keys = upload_image(file, folder='hero', create_responsive_versions=True)
            if s3_keys:
                model.image_s3_key = s3_keys.get('original')
                model.image_s3_key_small = s3_keys.get('small')
                model.image_s3_key_medium = s3_keys.get('medium')
                model.image_s3_key_large = s3_keys.get('large')


class AboutSectionAdminView(AdminModelView):
    """ Custom view for the About Section with image upload. """
    edit_template = 'admin/about_section_edit.html'
    form_extra_fields = { 'image_upload': FileField('Upload New Image') }
    form_columns = ['title', 'content_html', 'image_upload']
    
    
    # Assign explicit IDs to the title and content fields.
    form_widget_args = {
        'title': {
            'id': 'about_title'
        },
        'content_html': {
            'id': 'about_content'
        }
    }

    def edit_form(self, obj=None):
        form = super(AboutSectionAdminView, self).edit_form(obj)
        if obj and obj.image_s3_key:
            if form.image_upload.render_kw is None:
                form.image_upload.render_kw = {}
            form.image_upload.render_kw['data-current-image'] = generate_presigned_url(obj.image_s3_key)
        return form

    def on_model_change(self, form, model, is_created):
        file = request.files.get('image_upload')
        if file and file.filename:
            s3_keys = upload_image(file, folder='about', create_responsive_versions=True)
            if s3_keys:
                model.image_s3_key = s3_keys.get('original')
                model.image_s3_key_small = s3_keys.get('small')
                model.image_s3_key_medium = s3_keys.get('medium')
                model.image_s3_key_large = s3_keys.get('large')

class AnnouncementBannerAdminView(AdminModelView):
    """Custom Admin View for the Announcement Banner."""
    form = AnnouncementBannerForm
    column_list = ('is_active', 'main_text', 'featured_puppy')

    def on_model_change(self, form, model, is_created):
        selected_puppy = form.featured_puppy.data
        if selected_puppy:
            model.featured_puppy_id = selected_puppy.id
        else:
            model.featured_puppy_id = None