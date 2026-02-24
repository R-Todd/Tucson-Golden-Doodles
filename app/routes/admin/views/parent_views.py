# app/routes/admin/views/parent_views.py

from flask import request, flash, current_app
from wtforms.validators import ValidationError

from .base import AdminModelView
from app.utils.image_uploader import upload_image
from app.routes.admin.forms.parent_forms import ParentForm


class ParentAdminView(AdminModelView):
    """Custom Admin View for Parents with Bootstrap 5 templates and live preview."""

    # Template and Form Configuration
    list_template = 'admin/parent/list_bs5.html'
    create_template = 'admin/parent/create_bs5.html'
    edit_template = 'admin/parent/edit_bs5.html'
    form = ParentForm

    column_list = ['name', 'role', 'breed', 'is_active', 'is_guardian']

    form_widget_args = {
        'name': {'id': 'name'},
        'breed': {'id': 'breed'},
        'weight_kg': {'id': 'weight_kg'},
        'description': {'id': 'description', 'rows': 10},
        'image_upload': {'id': 'image_upload'},
        'alternate_image_upload_1': {'id': 'alternate_image_upload_1'},
        'alternate_image_upload_2': {'id': 'alternate_image_upload_2'},
        'alternate_image_upload_3': {'id': 'alternate_image_upload_3'},
        'alternate_image_upload_4': {'id': 'alternate_image_upload_4'},
    }

    def on_model_change(self, form, model, is_created):
        # Phase 4 hardening:
        # - upload_image returns (result, err). We must unpack it consistently.
        # - If rejected (.heic / invalid ext), show a flash message and abort save cleanly.
        # - Evict memoized s3_url(old_key) when keys change so images update immediately.
        # - Use a lazy import for cache to avoid circular imports at app startup.

        main_file = request.files.get('image_upload')
        if main_file and main_file.filename:
            # capture old keys for cache busting
            old_keys = [model.main_image_s3_key, model.main_image_s3_key_large]

            s3_keys, err = upload_image(main_file, folder='parents', create_responsive_versions=True)
            if err or not s3_keys:
                msg = err or "Parent image upload failed. Please upload a JPG/PNG."
                flash(msg, category="danger")
                raise ValidationError(msg)

            model.main_image_s3_key = s3_keys.get('original')
            model.main_image_s3_key_large = s3_keys.get('large')

            # Bust cached presigned URLs for old keys so updates show immediately
            s3_url_filter = current_app.jinja_env.filters.get("s3_url")
            if s3_url_filter:
                for k in old_keys:
                    if k:
                        try:
                            from app import cache  # lazy import avoids circular import
                            cache.delete_memoized(s3_url_filter, k)
                        except Exception:
                            pass

        alt_fields = [f'alternate_image_upload_{i}' for i in range(1, 5)]
        alt_model_attrs = [f'alternate_image_s3_key_{i}' for i in range(1, 5)]

        for i, field_name in enumerate(alt_fields):
            file = request.files.get(field_name)
            if file and file.filename:
                old_key = getattr(model, alt_model_attrs[i], None)

                key, err = upload_image(file, folder='parents_alternates')
                if err or not key:
                    msg = err or f"Alternate image {i + 1} upload failed. Please upload a JPG/PNG."
                    flash(msg, category="danger")
                    raise ValidationError(msg)

                setattr(model, alt_model_attrs[i], key)

                # Bust cached presigned URL for the previous key
                s3_url_filter = current_app.jinja_env.filters.get("s3_url")
                if s3_url_filter and old_key:
                    try:
                        from app import cache  # lazy import avoids circular import
                        cache.delete_memoized(s3_url_filter, old_key)
                    except Exception:
                        pass

        return super().on_model_change(form, model, is_created)