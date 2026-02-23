# app/routes/admin/views/puppy_views.py

from flask import request
from flask_wtf import FlaskForm
from wtforms.fields import FileField, SelectField, StringField
from wtforms.validators import InputRequired, DataRequired

from .base import AdminModelView
from app.models import Puppy, PuppyStatus, Litter, db
from app.utils.image_uploader import upload_image


class PuppyForm(FlaskForm):
    """Defines the custom form used for creating/editing Puppy records."""
    name = StringField("Name", validators=[DataRequired()])
    litter_id = SelectField("Litter", coerce=int, validators=[InputRequired()])
    status = SelectField("Status", choices=[(s.name, s.value) for s in PuppyStatus], validators=[DataRequired()])
    coat = StringField("Coat", validators=[])
    image_upload = FileField("Upload New Main Image")


class PuppyAdminView(AdminModelView):
    """Manages the admin interface for Puppy records with Bootstrap 5 templates."""

    list_template = 'admin/puppy/list_bs5.html'
    create_template = 'admin/puppy/create_bs5.html'
    edit_template = 'admin/puppy/edit_bs5.html'

    column_list = ('name', 'litter', 'status')

    form = PuppyForm

    form_widget_args = {
        'name': {'id': 'name'},
        'litter_id': {'id': 'litter_id'},
        'coat': {'id': 'coat'},
        'status': {'id': 'status'},
        'image_upload': {'id': 'image_upload'},
    }

    def _get_litter_choices(self):
        """Builds dropdown choices for litters."""
        litters = Litter.query.order_by(Litter.birth_date.desc()).all()
        return [(litter.id, litter.display_label) for litter in litters]

    def _populate_form_choices(self, form_instance, obj=None):
        """
        Populates the Litter dropdown.
        Ensures the dropdown choices are available in both create and edit views.
        """
        form_instance.litter_id.choices = self._get_litter_choices()

        # If editing and current puppy has a litter id not present (shouldn't happen),
        # keep it safe by injecting that value.
        if obj and obj.litter_id:
            existing_ids = {choice_id for (choice_id, _) in form_instance.litter_id.choices}
            if obj.litter_id not in existing_ids:
                litter = Litter.query.get(obj.litter_id)
                if litter:
                    form_instance.litter_id.choices.insert(0, (litter.id, litter.display_label))

    def create_form(self, obj=None):
        form = super().create_form(obj)
        self._populate_form_choices(form, obj=None)
        return form

    def edit_form(self, obj=None):
        form = super().edit_form(obj)
        self._populate_form_choices(form, obj=obj)
        return form

    def on_model_change(self, form, model, is_created):
        """
        Saves form data into the Puppy model.
        Handles image upload if a new image is provided.
        """
        model.name = form.name.data
        model.litter_id = form.litter_id.data
        model.status = PuppyStatus[form.status.data]
        model.coat = form.coat.data

        if form.image_upload.data:
            upload = form.image_upload.data
            model.main_image_s3_key = upload_image(upload, folder="puppies")

        db.session.add(model)
        db.session.commit()
