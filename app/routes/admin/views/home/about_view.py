# app/routes/admin/views/home/about_view.py

from flask import request, flash, current_app
from wtforms.fields import FileField
from wtforms.validators import ValidationError

from ..base import AdminModelView
from app.utils.image_uploader import upload_image


class AboutSectionAdminView(AdminModelView):
    """ Custom AdminModelView for the About Section using Bootstrap 5 templates. """
    can_create = True
    can_edit = True
    can_delete = True

    # The 'form_overrides' line has been removed to disable CKEditor.
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
    # Add widget arguments for the new standard textarea.
    form_widget_args = {
        'title': {'id': 'about_title'},
        'content_html': {
            'id': 'content_html',
            'rows': 10,
            'class': 'form-control'
        }
    }

    def on_model_change(self, form, model, is_created):
        """ Handle the S3 image upload when the model is saved. """
        file = request.files.get('image_upload')
        if file and file.filename:
            # Phase 4 hardening:
            # - upload_image returns (result, err). We must unpack it.
            # - If rejected (.heic / invalid ext), flash + abort save cleanly.
            # - Evict memoized s3_url(old_key) so updated images show immediately.
            # - Use lazy import for cache to avoid circular imports at startup.
            old_keys = [
                getattr(model, "image_s3_key", None),
                getattr(model, "image_s3_key_small", None),
                getattr(model, "image_s3_key_medium", None),
                getattr(model, "image_s3_key_large", None),
            ]

            s3_keys, err = upload_image(file, folder='about', create_responsive_versions=True)
            if err or not s3_keys:
                msg = err or "About image upload failed. Please upload a JPG/PNG."
                flash(msg, category="danger")
                raise ValidationError(msg)

            model.image_s3_key = s3_keys.get('original')
            model.image_s3_key_small = s3_keys.get('small')
            model.image_s3_key_medium = s3_keys.get('medium')
            model.image_s3_key_large = s3_keys.get('large')

            s3_url_filter = current_app.jinja_env.filters.get("s3_url")
            if s3_url_filter:
                for k in old_keys:
                    if k:
                        try:
                            from app import cache  # lazy import avoids circular import
                            cache.delete_memoized(s3_url_filter, k)
                        except Exception:
                            pass

        return super().on_model_change(form, model, is_created)