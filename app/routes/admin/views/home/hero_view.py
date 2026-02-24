# app/routes/admin/views/home/hero_view.py

from flask import request, flash, current_app
from wtforms.fields import FileField
from wtforms.validators import ValidationError

from ..base import AdminModelView
from app.utils.image_uploader import upload_image


class HeroSectionAdminView(AdminModelView):
    """ Custom view for the Hero Section with image upload and BS5 templates. """

    # --- Bootstrap 5 Template Configuration ---
    list_template = 'admin/hero/list_bs5.html'
    create_template = 'admin/hero/create_bs5.html'
    edit_template = 'admin/hero/edit_bs5.html'

    # --- Action Buttons ---
    can_create = True
    can_edit = True
    can_delete = True

    # --- List View ---
    column_list = ('main_title', 'subtitle', 'description')

    # --- Form View ---
    form_columns = [
        'main_title', 'subtitle', 'description', 'scroll_text_main',
        'scroll_text_secondary', 'image_upload'
    ]
    form_extra_fields = {
        'image_upload': FileField('Upload New Background Image (Recommended: 1920x1080px)')
    }
    form_widget_args = {
        'main_title': {'id': 'main_title'},
        'subtitle': {'id': 'subtitle'},
        'description': {'id': 'description'},
        'scroll_text_main': {'id': 'scroll_text_main'},
        'scroll_text_secondary': {'id': 'scroll_text_secondary'},
    }

    def on_model_change(self, form, model, is_created):
        """Handle the S3 image upload when the model is saved."""
        file = request.files.get("image_upload")
        if file and file.filename:
            # Capture old keys so we can bust cached presigned URLs (avoid "silent stale" hero)
            old_keys = [
                model.image_s3_key,
                model.image_s3_key_small,
                model.image_s3_key_medium,
                model.image_s3_key_large,
            ]

            s3_keys, err = upload_image(file, folder="hero", create_responsive_versions=True)

            if err or not s3_keys:
                # Show a friendly UI banner and keep the user on the form page.
                msg = err or "Hero upload failed. Please try a different image."
                flash(msg, category="danger")
                raise ValidationError(msg)

            model.image_s3_key = s3_keys.get("original")
            model.image_s3_key_small = s3_keys.get("small")
            model.image_s3_key_medium = s3_keys.get("medium")
            model.image_s3_key_large = s3_keys.get("large")

            # Bust cached presigned URLs for old keys so the new hero shows immediately
            s3_url_filter = current_app.jinja_env.filters.get("s3_url")
            if s3_url_filter:
                for k in old_keys:
                    if k:
                        try:
                            from app import cache
                             # lazy import prevents circular import during app startup
                            cache.delete_memoized(s3_url_filter, k)
                        except Exception:
                            # Never block admin save due to cache eviction issues
                            pass

        return super().on_model_change(form, model, is_created)