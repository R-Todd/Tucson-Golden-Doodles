# app/routes/admin/views/home/gallery_view.py

from flask import request, flash, current_app
from wtforms.fields import FileField
from wtforms.validators import ValidationError

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
        # Phase 4: don't raise ValueError (which can look like a 500).
        # Instead, flash + ValidationError so admin sees a clean message.
        if is_created and not file:
            msg = "An image upload is required to create a new gallery item."
            flash(msg, category="danger")
            raise ValidationError(msg)

        if file and file.filename:
            # Phase 4 hardening:
            # - upload_image returns (result, err). We must unpack it.
            # - If rejected (.heic / invalid ext), flash + abort save cleanly.
            # - Evict memoized s3_url(old_key) when keys change so the new image shows immediately.
            # - Use lazy import for cache to avoid circular imports at startup.
            old_key = getattr(model, "image_s3_key", None)

            # Use the simple uploader; no responsive versions needed for the main gallery.
            s3_key, err = upload_image(file, folder='gallery')

            if err or not s3_key:
                msg = err or "Gallery image upload failed. Please upload a JPG/PNG."
                flash(msg, category="danger")
                raise ValidationError(msg)

            model.image_s3_key = s3_key

            # Bust cached presigned URL for the previous key
            s3_url_filter = current_app.jinja_env.filters.get("s3_url")
            if s3_url_filter and old_key:
                try:
                    from app import cache  # lazy import avoids circular import
                    cache.delete_memoized(s3_url_filter, old_key)
                except Exception:
                    pass

        return super().on_model_change(form, model, is_created)