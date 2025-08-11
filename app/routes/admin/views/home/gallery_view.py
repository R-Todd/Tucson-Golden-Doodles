# app/routes/admin/views/home/gallery_view.py

from flask import request
from wtforms.fields import FileField
from ..base import AdminModelView
from app.utils.image_uploader import upload_image

class GalleryImageAdminView(AdminModelView):
    """ Custom Admin View for Gallery Images with Bootstrap 5 templates and live preview. """

    # --- Template Configuration ---
    list_template = 'admin/gallery/list_bs5.html'
    create_template = 'admin/gallery/create_bs5.html'
    edit_template = 'admin/gallery/edit_bs5.html'

    # --- List View ---
    column_list = ('image_s3_key', 'caption', 'sort_order')
    column_labels = {'image_s3_key': 'Image'}
    
    # --- Form View ---
    form_columns = ('caption', 'sort_order', 'image_upload')
    form_extra_fields = {
        'image_upload': FileField('Upload Image (Required on create)')
    }
    form_widget_args = {
        'caption': {'id': 'caption'},
        'sort_order': {'id': 'sort_order'}
    }

    def on_model_change(self, form, model, is_created):
        """ Handles the S3 image upload when a gallery item is saved. """
        file = request.files.get('image_upload')
        
        # On creation, an image is required.
        if is_created and not file:
            raise ValueError("An image upload is required to create a new gallery item.")

        if file and file.filename:
            # Use the simple uploader; no responsive versions needed for the main gallery.
            s3_key = upload_image(file, folder='gallery')
            if s3_key:
                model.image_s3_key = s3_key