# app/routes/admin/views/litter_views.py

from flask_wtf import FlaskForm
from wtforms import DateField, SelectField, StringField, TextAreaField
from wtforms.validators import DataRequired, Optional, InputRequired

from .base import AdminModelView
from app.models import Parent, ParentRole


class LitterForm(FlaskForm):
    """Defines the fields and validation for creating/editing Litter records."""

    mom_id = SelectField(
        "Mother (Dam)",
        coerce=int,
        validators=[InputRequired(message="Please select the mother (dam).")]
    )

    dad_id = SelectField(
        "Father (Sire)",
        coerce=int,
        validators=[InputRequired(message="Please select the father (sire).")]
    )

    birth_date = DateField("Born On", validators=[DataRequired()])

    breed_name = StringField("Breed Name", validators=[Optional()])

    expected_weight = StringField("Expected Weight", validators=[Optional()])

    description = TextAreaField("Description", validators=[Optional()])


class LitterAdminView(AdminModelView):
    """Admin interface for managing Litters (shared litter info + parents)."""

    list_template = "admin/litter/list_bs5.html"
    create_template = "admin/litter/create_bs5.html"
    edit_template = "admin/litter/edit_bs5.html"

    # NOTE: "mother" and "father" come from Parent backrefs on Litter (as used elsewhere in your templates)
    column_list = ("birth_date", "mother", "father", "breed_name", "expected_weight")

    form = LitterForm

    form_widget_args = {
        "mom_id": {"id": "mom_id"},
        "dad_id": {"id": "dad_id"},
        "birth_date": {"id": "birth_date"},
        "breed_name": {"id": "breed_name"},
        "expected_weight": {"id": "expected_weight"},
        "description": {"id": "description", "rows": 8},
    }

    def _get_parent_choices(self, role: ParentRole):
        """Builds dropdown choices for parents filtered by role."""
        parents = Parent.query.filter_by(role=role).order_by(Parent.name.asc()).all()
        return [(p.id, p.name) for p in parents]

    def _populate_form_choices(self, form_instance, obj=None):
        """
        Populate mom/dad dropdowns.
        Only pre-select the current values on GET (not on POST),
        so edits don't get overwritten.
        """
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

    def on_model_change(self, form, model, is_created):
        """Persist relationships and shared litter fields."""
        model.mom_id = form.mom_id.data
        model.dad_id = form.dad_id.data
        model.birth_date = form.birth_date.data
        model.breed_name = (form.breed_name.data or None)
        model.expected_weight = (form.expected_weight.data or None)
        model.description = (form.description.data or None)
