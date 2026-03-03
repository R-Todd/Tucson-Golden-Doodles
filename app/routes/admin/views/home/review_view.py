# app/routes/admin/views/home/review_view.py

from ..base import AdminModelView
from flask import request, flash
from wtforms import FileField
from wtforms.validators import ValidationError

from app.utils.image_uploader import upload_image
from app.models import db, ReviewImage


class ReviewAdminView(AdminModelView):
    """A custom view for Reviews that uses an organized Bootstrap 5 template."""

    can_create = True
    can_edit = True
    can_delete = True

    # Template configuration
    list_template = 'admin/reviews/list_bs5.html'
    create_template = 'admin/reviews/create_bs5.html'
    edit_template = 'admin/reviews/edit_bs5.html'

    # Specify columns to display in the list view
    column_list = ('sort_order', 'author_name', 'is_featured', 'testimonial_text')
    column_default_sort = ('sort_order', True)

    # Specify the fields to include in the create and edit forms
    form_columns = ('sort_order', 'author_name', 'testimonial_text', 'is_featured', 'image_upload')

    # Add a "Choose file" upload to the Review form (matches Parents pattern)
    form_extra_fields = {
        'image_upload': FileField('Add Review Image')
    }

    # Add IDs to the form widgets so
    # the preview JavaScript can find them.
    form_widget_args = {
        'sort_order': {
            'id': 'sort_order'
        },
        'author_name': {
            'id': 'author_name'
        },
        'testimonial_text': {
            'id': 'testimonial_text',
            'rows': 10
        },
        'image_upload': {
            'id': 'image_upload'
        },
    }

    def on_model_change(self, form, model, is_created):
        """
        If an image is uploaded on the Review create/edit form, upload to S3 and
        create a ReviewImage row linked to this review.

        Note: This allows multiple images by editing the review again and uploading another.
        For advanced management (reorder/captions), use Reviews -> Images.
        """
        # ------------------------------------------------------
        # Existing images: update sort orders + handle deletions
        # ------------------------------------------------------
        # We accept inputs named:
        #   review_image_sort_<id>   => integer sort order
        #   review_image_delete_<id> => "1" when checked
        #
        # These inputs are injected into the main form by JS in edit_bs5.html.
        image_by_id = {img.id: img for img in (model.images or []) if getattr(img, "id", None)}

        # Apply sort updates
        for key, value in request.form.items():
            if not key.startswith("review_image_sort_"):
                continue
            try:
                image_id = int(key.replace("review_image_sort_", "").strip())
            except ValueError:
                continue

            img = image_by_id.get(image_id)
            if not img:
                continue

            try:
                img.sort_order = int(value)
            except (TypeError, ValueError):
                # ignore invalid sort inputs
                continue

        # Apply deletions (deletions win)
        for key, value in request.form.items():
            if not key.startswith("review_image_delete_"):
                continue
            if str(value) != "1":
                continue
            try:
                image_id = int(key.replace("review_image_delete_", "").strip())
            except ValueError:
                continue

            img = image_by_id.get(image_id)
            if img:
                db.session.delete(img)

        file = request.files.get('image_upload')
        if file and file.filename:
            key, err = upload_image(file, folder='reviews')
            if err or not key:
                msg = err or "Review image upload failed. Please upload a JPG/PNG."
                flash(msg, category="danger")
                raise ValidationError(msg)

            # Append image at the end by default
            existing = model.images or []
            next_sort = 0
            if existing:
                try:
                    next_sort = max((img.sort_order or 0) for img in existing) + 1
                except Exception:
                    next_sort = len(existing)

            model.images.append(ReviewImage(s3_key=key, sort_order=next_sort))

        return super().on_model_change(form, model, is_created)