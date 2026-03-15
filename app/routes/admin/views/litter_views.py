# app/routes/admin/views/litter_views.py

from flask import request, flash, current_app
from flask_wtf import FlaskForm
from wtforms import DateField, SelectField, StringField, TextAreaField
from wtforms.fields import FileField
from wtforms.validators import DataRequired, Optional, InputRequired, ValidationError

from .base import AdminModelView
from app.models import Parent, ParentRole
from app.utils.image_uploader import upload_image


class LitterForm(FlaskForm):
    """Defines the fields and validation for creating/editing Litter records."""

    mom_id = SelectField(
        "Mother",
        coerce=int,
        validators=[InputRequired(message="Please select a mother.")]
    )

    dad_id = SelectField(
        "Father",
        coerce=int,
        validators=[InputRequired(message="Please select a father.")]
    )

    expected_birth_date = DateField("Expected Birth Date", validators=[Optional()])

    birth_date = DateField("Born On", validators=[Optional()])

    breed_name = StringField("Breed Name", validators=[Optional()])

    expected_weight = StringField(
        "Expected Weight (lbs)",
        validators=[Optional()],
        render_kw={"placeholder": "e.g. 25-35 lbs"},
    )

    description = TextAreaField("Description", validators=[Optional()])

    status_mode = SelectField(
        "Litter Stage",
        choices=[
            ("upcoming", "Upcoming"),
            ("current", "Current"),
            ("past", "Past"),
        ],
        default="upcoming",
        validators=[DataRequired()],
    )

    image_upload = FileField("Upload Main Litter Image")

    def validate(self, extra_validators=None):
        if not super().validate(extra_validators=extra_validators):
            return False

        stage = (self.status_mode.data or "upcoming").strip().lower()

        if stage == "upcoming":
            if not self.expected_birth_date.data:
                self.expected_birth_date.errors.append("Upcoming litters require an expected birth date.")
                return False
            return True

        if stage == "current":
            effective_birth_date = self.birth_date.data or self.expected_birth_date.data
            if not effective_birth_date:
                self.birth_date.errors.append("Current litters require a birth date or an expected birth date to convert.")
                return False
            return True

        if not self.birth_date.data:
            self.birth_date.errors.append("Current and past litters require a birth date.")
            return False

        return True


class LitterAdminView(AdminModelView):
    """Admin interface for managing Litters (shared litter info + parents)."""

    list_template = "admin/litter/list_bs5.html"
    create_template = "admin/litter/create_bs5.html"
    edit_template = "admin/litter/edit_bs5.html"

    column_list = ("status_mode", "expected_birth_date", "birth_date", "mother", "father", "breed_name", "expected_weight")

    form = LitterForm

    form_widget_args = {
        "mom_id": {"id": "mom_id"},
        "dad_id": {"id": "dad_id"},
        "expected_birth_date": {"id": "expected_birth_date"},
        "birth_date": {"id": "birth_date"},
        "breed_name": {"id": "breed_name"},
        "expected_weight": {"id": "expected_weight"},
        "description": {"id": "description", "rows": 8},
        "status_mode": {"id": "status_mode"},
        "image_upload": {"id": "image_upload"},
    }

    def _get_parent_choices(self, role: ParentRole):
        parents = Parent.query.filter_by(role=role).order_by(Parent.name.asc()).all()
        return [(p.id, p.name) for p in parents]

    def _populate_form_choices(self, form_instance, obj=None):
        form_instance.mom_id.choices = self._get_parent_choices(ParentRole.MOM)
        form_instance.dad_id.choices = self._get_parent_choices(ParentRole.DAD)

        if (not form_instance.is_submitted()) and obj:
            if getattr(obj, "mom_id", None):
                form_instance.mom_id.data = obj.mom_id
            if getattr(obj, "dad_id", None):
                form_instance.dad_id.data = obj.dad_id

        return form_instance

    def create_form(self):
        form_instance = super().create_form()
        return self._populate_form_choices(form_instance)

    def edit_form(self, obj=None):
        form_instance = super().edit_form(obj)
        return self._populate_form_choices(form_instance, obj)

    def _normalize_stage(self, value):
        stage = (value or "upcoming").strip().lower()
        return stage if stage in {"upcoming", "current", "past"} else "upcoming"

    def on_model_change(self, form, model, is_created):
        """Persist relationships and shared litter fields + handle cover image upload."""
        model.mom_id = form.mom_id.data
        model.dad_id = form.dad_id.data

        stage = self._normalize_stage(form.status_mode.data)

        expected_birth_date = form.expected_birth_date.data
        birth_date = form.birth_date.data

        if stage == "current":
            if not birth_date and expected_birth_date:
                birth_date = expected_birth_date
            expected_birth_date = None
        elif stage == "past":
            expected_birth_date = None

        model.expected_birth_date = expected_birth_date
        model.birth_date = birth_date
        model.breed_name = (form.breed_name.data or None)
        model.expected_weight = (form.expected_weight.data or None)
        model.description = (form.description.data or None)
        model.status_mode = stage

        upload = request.files.get("image_upload")
        if upload and upload.filename:
            old_key = getattr(model, "main_image_s3_key", None)

            new_key, err = upload_image(upload, folder="litters")
            if err or not new_key:
                msg = err or "Litter image upload failed. Please upload a JPG/PNG."
                flash(msg, category="danger")
                raise ValidationError(msg)

            model.main_image_s3_key = new_key

            s3_url_filter = current_app.jinja_env.filters.get("s3_url")
            if s3_url_filter and old_key:
                try:
                    from app import cache
                    cache.delete_memoized(s3_url_filter, old_key)
                except Exception:
                    pass

        return super().on_model_change(form, model, is_created)