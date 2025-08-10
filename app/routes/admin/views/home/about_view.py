# app/routes/admin/views/home/about_view.py

from flask import request
from wtforms.fields import FileField
from ..base import AdminModelView
from app.utils.image_uploader import upload_image

class AboutSectionAdminView(AdminModelView):
    """ Custom AdminModelView for the About Section using Bootstrap 5 templates. """

    # --- Bootstrap 5 Template Configuration ---
    # Point the view to the new, isolated BS5 templates.
    list_template = 'admin/about/list_bs5.html'
    create_template = 'admin/about/create_bs5.html'
    edit_template = 'admin/about/edit_bs5.html'

    # --- List View Configuration ---
    # Define columns to show in the list view.
    column_list = ('title',)
    
    # --- Form Configuration ---
    # Define fields for the create/edit forms.
    form_columns = [
        'title', 
        'content_html', 
        'image_upload'
    ]
    # Add a file upload field to the form.
    form_extra_fields = {
        'image_upload': FileField('Upload New Image')
    }
    # Assign IDs to form fields for the live preview JavaScript to target.
    form_widget_args = {
        'title': { 'id': 'about_title' },
        'content_html': { 'id': 'about_content_html', 'rows': 10 }
    }

    def on_model_change(self, form, model, is_created):
        """
        Handle the S3 image upload when the model is saved.
        This logic is moved from the old site_views.py.
        """
        file = request.files.get('image_upload')
        if file and file.filename:
            # Upload the image and get back a dictionary of S3 keys.
            s3_keys = upload_image(file, folder='about', create_responsive_versions=True)
            if s3_keys:
                model.image_s3_key = s3_keys.get('original')
                model.image_s3_key_small = s3_keys.get('small')
                model.image_s3_key_medium = s3_keys.get('medium')
                model.image_s3_key_large = s3_keys.get('large')