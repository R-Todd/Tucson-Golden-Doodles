# app/routes/admin/views/home/gallery_view.py

from flask import request, flash, current_app, redirect
from flask_admin import expose
from wtforms.fields import FileField
from wtforms.validators import ValidationError
from sqlalchemy import func

from ..base import AdminModelView
from app.utils.image_uploader import upload_image


class GalleryImageAdminView(AdminModelView):
    """ Custom Admin View for Gallery Images with Bootstrap 5 templates and live preview. """

    # --- Template Configuration ---
    list_template = 'admin/gallery/list_bs5.html'
    create_template = 'admin/gallery/create_bs5.html'
    edit_template = 'admin/gallery/edit_bs5.html'

    column_default_sort = ('sort_order', True)

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

    def get_query(self):
        return super().get_query().order_by(self.model.sort_order.asc(), self.model.id.desc())

    def _normalize_sort_orders(self, items):
        for index, item in enumerate(items):
            item.sort_order = index

    def _ordered_items(self):
        return (
            self.session.query(self.model)
            .order_by(self.model.sort_order.asc(), self.model.id.asc())
            .all()
        )

    def _insert_item_at_position(self, item, position):
        items = [existing for existing in self._ordered_items() if existing.id != getattr(item, 'id', None)]

        if position is None:
            position = 0

        position = max(0, min(position, len(items)))
        items.insert(position, item)
        self._normalize_sort_orders(items)

    @expose('/quick-add/', methods=('POST',))
    def quick_add_view(self):
        if not self.is_accessible():
            return self.inaccessible_callback('quick_add_view')

        file = request.files.get('quick_image_upload')
        caption = (request.form.get('quick_caption') or '').strip() or None
        sort_raw = (request.form.get('quick_sort_order') or '').strip()

        if not file or not file.filename:
            flash('Please choose an image to upload.', 'danger')
            return redirect(self.get_url('.index_view'))

        try:
            requested_position = int(sort_raw) if sort_raw else 0
        except ValueError:
            flash('Sort order must be a whole number.', 'danger')
            return redirect(self.get_url('.index_view'))

        s3_key, err = upload_image(file, folder='gallery')
        if err or not s3_key:
            flash(err or 'Gallery image upload failed. Please upload a JPG/PNG.', 'danger')
            return redirect(self.get_url('.index_view'))

        item = self.model(image_s3_key=s3_key, caption=caption, sort_order=0)
        self.session.add(item)
        self._insert_item_at_position(item, requested_position)
        self.session.commit()
        flash('Gallery image added.', 'success')
        return redirect(self.get_url('.index_view'))

    @expose('/quick-update/<int:item_id>/', methods=('POST',))
    def quick_update_view(self, item_id):
        if not self.is_accessible():
            return self.inaccessible_callback('quick_update_view')

        item = self.session.get(self.model, item_id)
        if item is None:
            flash('Gallery image not found.', 'danger')
            return redirect(self.get_url('.index_view'))

        if request.form.get('delete_image') == 'y':
            self.session.delete(item)
            self.session.commit()
            self._normalize_sort_orders(self._ordered_items())
            self.session.commit()
            flash('Gallery image deleted.', 'success')
            return redirect(self.get_url('.index_view'))

        try:
            requested_position = int((request.form.get('sort_order') or item.sort_order or 0))
        except ValueError:
            flash('Sort order must be a whole number.', 'danger')
            return redirect(self.get_url('.index_view'))

        item.caption = (request.form.get('caption') or '').strip() or None
        self._insert_item_at_position(item, requested_position)
        self.session.commit()
        flash('Gallery image updated.', 'success')
        return redirect(self.get_url('.index_view'))

    @expose('/quick-reorder/', methods=('POST',))
    def quick_reorder_view(self):
        if not self.is_accessible():
            return self.inaccessible_callback('quick_reorder_view')

        ordered_ids = request.form.getlist('ordered_ids[]')
        if not ordered_ids:
            flash('No gallery order was provided.', 'danger')
            return redirect(self.get_url('.index_view'))

        items = []
        for index, item_id in enumerate(ordered_ids):
            item = self.session.get(self.model, int(item_id))
            if item is not None:
                items.append(item)

        self._normalize_sort_orders(items)

        self.session.commit()
        flash('Gallery order updated.', 'success')
        return redirect(self.get_url('.index_view'))

    def on_model_change(self, form, model, is_created):
        """ Handles the S3 image upload when a gallery item is saved. """
        file = request.files.get('image_upload')

        if is_created and not file:
            msg = "An image upload is required to create a new gallery item."
            flash(msg, category="danger")
            raise ValidationError(msg)

        if file and file.filename:
            old_key = getattr(model, "image_s3_key", None)
            s3_key, err = upload_image(file, folder='gallery')

            if err or not s3_key:
                msg = err or "Gallery image upload failed. Please upload a JPG/PNG."
                flash(msg, category="danger")
                raise ValidationError(msg)

            model.image_s3_key = s3_key

            s3_url_filter = current_app.jinja_env.filters.get("s3_url")
            if s3_url_filter and old_key:
                try:
                    from app import cache
                    cache.delete_memoized(s3_url_filter, old_key)
                except Exception:
                    pass

        return super().on_model_change(form, model, is_created)