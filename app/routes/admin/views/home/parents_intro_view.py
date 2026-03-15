# app/routes/admin/views/home/parents_intro_view.py

from flask import request, flash, current_app
from flask import redirect
from flask_admin import expose
from wtforms.fields import FileField
from wtforms.validators import ValidationError

from ..base import AdminModelView
from app.utils.image_uploader import upload_image


class ParentsPageIntroAdminView(AdminModelView):
    """
    Admin view for the Parents page intro content (main image + editable HTML).
    Mirrors the same pattern used by other editable site sections.
    """

    can_create = True
    can_edit = True
    can_delete = False

    # Bootstrap 5 templates for this model.
    list_template = 'admin/parents_intro/list_bs5.html'
    create_template = 'admin/parents_intro/create_bs5.html'
    edit_template = 'admin/parents_intro/edit_bs5.html'

    column_list = ('title',)

    form_columns = [
        'is_active',
        'title',
        'content_html',
        'image_upload'
    ]
    form_extra_fields = {
        'image_upload': FileField('Upload New Parents Page Image')
    }

    form_widget_args = {
        'is_active': {'id': 'parents_intro_is_active'},
        'title': {'id': 'parents_intro_title'},
        'content_html': {
            'id': 'parents_intro_content_html',
            'rows': 10,
            'class': 'form-control'
        }
    }

    def _get_singleton(self):
        """Return the first existing ParentsPageIntro record, if any."""
        try:
            return self.session.query(self.model).order_by(self.model.id.asc()).first()
        except Exception:
            return None

    @expose('/new/', methods=('GET', 'POST'))
    def create_view(self):
        """
        Enforce singleton: if a record already exists, redirect Create -> Edit.
        """
        existing = self._get_singleton()
        if existing:
            return redirect(self.get_url('.edit_view', id=existing.id))
        return super().create_view()

    @expose('/')
    def index_view(self):
        """
        Enforce singleton: if a record exists, redirect List -> Edit.
        """
        existing = self._get_singleton()
        if existing:
            return redirect(self.get_url('.edit_view', id=existing.id))
        return super().index_view()

    def on_model_change(self, form, model, is_created):
        """Handle the S3 image upload when the model is saved."""
        file = request.files.get('image_upload')
        if file and file.filename:
            # Capture old keys so we can bust cached presigned URLs.
            old_keys = [
                getattr(model, "image_s3_key", None),
                getattr(model, "image_s3_key_small", None),
                getattr(model, "image_s3_key_medium", None),
                getattr(model, "image_s3_key_large", None),
            ]

            s3_keys, err = upload_image(file, folder='parents', create_responsive_versions=True)
            if err or not s3_keys:
                msg = err or "Parents page image upload failed. Please upload a JPG/PNG."
                flash(msg, category="danger")
                raise ValidationError(msg)

            model.image_s3_key = s3_keys.get('original')
            model.image_s3_key_small = s3_keys.get('small')
            model.image_s3_key_medium = s3_keys.get('medium')
            model.image_s3_key_large = s3_keys.get('large')

            # Bust cached presigned URLs for old keys so the new image shows immediately.
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