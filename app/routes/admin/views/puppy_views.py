# app/routes/admin/views/puppy_views.py

from flask import request, flash, current_app
from flask_wtf import FlaskForm
from wtforms.fields import FileField, SelectField, StringField
from wtforms.validators import InputRequired, DataRequired, ValidationError

from .base import AdminModelView
from app.models import Puppy, PuppyStatus, Litter, db
from app.utils.image_uploader import upload_image


class PuppyForm(FlaskForm):
    """Defines the custom form used for creating/editing Puppy records."""
    GENDER_CHOICES = [
        ("", "Select Gender"),
        ("Male", "Male"),
        ("Female", "Female"),
    ]

    name = StringField("Name", validators=[DataRequired()])
    litter_id = SelectField("Litter", coerce=int, validators=[InputRequired()])
    gender = SelectField("Gender", choices=GENDER_CHOICES, validators=[])
    status = SelectField("Status", choices=[(s.name, s.value) for s in PuppyStatus], validators=[DataRequired()])
    coat = StringField("Coat", validators=[])
    image_upload = FileField("Upload New Main Image")


class PuppyAdminView(AdminModelView):
    """Manages the admin interface for Puppy records with Bootstrap 5 templates."""

    list_template = 'admin/puppy/list_bs5.html'
    create_template = 'admin/puppy/create_bs5.html'
    edit_template = 'admin/puppy/edit_bs5.html'

    column_list = ('name', 'gender', 'litter', 'status')

    form = PuppyForm

    form_widget_args = {
        'name': {'id': 'name'},
        'litter_id': {'id': 'litter_id'},
        'coat': {'id': 'coat'},
        'gender': {'id': 'gender'},
        'status': {'id': 'status'},
        'image_upload': {'id': 'image_upload'},
    }

    def _get_litter_choices(self, include_upcoming=True):
        """Build dropdown choices for litters.

        For puppy creation, upcoming litters should be excluded so new puppies
        can only be added to current/past litters. For editing, we keep the full
        list so existing records are not disrupted.
        """
        litters = Litter.query.order_by(Litter.birth_date.desc()).all()
        if not include_upcoming:
            litters = [litter for litter in litters if not litter.is_upcoming]
        return [(litter.id, litter.display_label) for litter in litters]

    def _populate_form_choices(self, form_instance, obj=None, include_upcoming=True):
        """
        Populates the Litter dropdown.
        Ensures the dropdown choices are available in both create and edit views.
        """
        form_instance.litter_id.choices = self._get_litter_choices(include_upcoming=include_upcoming)

        if obj and obj.litter_id:
            existing_ids = {choice_id for (choice_id, _) in form_instance.litter_id.choices}
            if obj.litter_id not in existing_ids:
                litter = Litter.query.get(obj.litter_id)
                if litter:
                    form_instance.litter_id.choices.insert(0, (litter.id, litter.display_label))

    def _get_requested_litter_id(self):
        """Read an optional litter_id from the query string."""
        raw_litter_id = request.args.get("litter_id", type=int)
        if not raw_litter_id:
            return None

        litter = Litter.query.get(raw_litter_id)
        return litter.id if litter else None

    def create_form(self, obj=None):
        form = super().create_form(obj)
        self._populate_form_choices(form, obj=None, include_upcoming=False)

        requested_litter_id = self._get_requested_litter_id()
        if requested_litter_id and not form.is_submitted():
            requested_litter = Litter.query.get(requested_litter_id)
            if requested_litter and requested_litter.is_upcoming:
                flash(
                    'Puppies cannot be added to an upcoming litter. '
                    'Change the litter stage to Current and save the litter first.',
                    category='warning'
                )
            else:
                form.litter_id.data = requested_litter_id

        return form

    def edit_form(self, obj=None):
        form = super().edit_form(obj)
        self._populate_form_choices(form, obj=obj, include_upcoming=True)
        return form

    def on_model_change(self, form, model, is_created):
        """
        Saves form data into the Puppy model.
        Handles image upload if a new image is provided.
        """
        selected_litter = Litter.query.get(form.litter_id.data)

        if not selected_litter:
            raise ValidationError("Please select a valid litter.")

        if is_created and selected_litter.is_upcoming:
            msg = (
                "Puppies cannot be added to an upcoming litter. "
                "Change the litter stage to Current and save the litter first."
            )
            flash(msg, category="warning")
            raise ValidationError(msg)

        model.name = form.name.data
        model.litter_id = form.litter_id.data
        model.gender = form.gender.data or None
        model.status = PuppyStatus[form.status.data]
        model.coat = form.coat.data

        # Phase 4 hardening:
        # - upload_image returns (result, err). We must unpack it.
        # - If rejected (.heic / invalid ext), show flash + abort save cleanly.
        # - Evict memoized s3_url(old_key) when keys change so new image shows immediately.
        # - Use lazy import for cache to avoid circular imports at startup.
        if form.image_upload.data:
            upload = form.image_upload.data
            old_key = getattr(model, "main_image_s3_key", None)

            new_key, err = upload_image(upload, folder="puppies")
            if err or not new_key:
                msg = err or "Puppy image upload failed. Please upload a JPG/PNG."
                flash(msg, category="danger")
                raise ValidationError(msg)

            model.main_image_s3_key = new_key

            s3_url_filter = current_app.jinja_env.filters.get("s3_url")
            if s3_url_filter and old_key:
                try:
                    from app import cache  # lazy import avoids circular import
                    cache.delete_memoized(s3_url_filter, old_key)
                except Exception:
                    pass

        # Preserve original behavior: this view commits explicitly.
        db.session.add(model)
        db.session.commit()