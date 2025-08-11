# app/routes/admin/views/home/about_view.py

from flask import request
from wtforms.fields import FileField

# Import the rich-text editor field from Flask-Admin.
from flask_ckeditor import CKEditorField

from ..base import AdminModelView
from app.utils.image_uploader import upload_image

class AboutSectionAdminView(AdminModelView):
    """ Custom AdminModelView for the About Section using Bootstrap 5 templates. """
    can_create = True
    can_edit = True
    can_delete = True

    # --- CKEditorField ---
    # Override the form field for 'content_html' to use the CKEditor widget.
    form_overrides = dict(content_html=CKEditorField)


    list_template = 'admin/about/list_bs5.html'
    create_template = 'admin/about/create_bs5.html'
    edit_template = 'admin/about/edit_bs5.html'
    column_list = ('title',)
    form_columns = [
        'title', 
        'content_html', 
        'image_upload'
    ]
    form_extra_fields = {
        'image_upload': FileField('Upload New Image')
    }
    # We no longer need to style 'content_html' here, so it's removed.
    form_widget_args = {
        'title': { 'id': 'about_title' }
    }

    def on_model_change(self, form, model, is_created):
        """ Handle the S3 image upload when the model is saved. """
        file = request.files.get('image_upload')
        if file and file.filename:
            s3_keys = upload_image(file, folder='about', create_responsive_versions=True)
            if s3_keys:
                model.image_s3_key = s3_keys.get('original')
                model.image_s3_key_small = s3_keys.get('small')
                model.image_s3_key_medium = s3_keys.get('medium')
                model.image_s3_key_large = s3_keys.get('large')