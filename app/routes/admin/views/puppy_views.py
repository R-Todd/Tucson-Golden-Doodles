# app/routes/admin/views/puppy_views.py

from flask import request
from flask_wtf import FlaskForm
from wtforms.fields import FileField, SelectField, StringField
from wtforms.validators import InputRequired, DataRequired

from .base import AdminModelView
from app.models import Puppy, PuppyStatus, Litter, db
from app.utils.image_uploader import upload_image


class PuppyForm(FlaskForm):
    """Defines the fields and validation for the puppy creation and edit forms."""

    name = StringField('Name', validators=[DataRequired()])

    litter_id = SelectField(
        'Litter',
        coerce=int,
        validators=[InputRequired(message="Please select a litter.")]
    )

    coat = StringField('Coat')

    status = SelectField(
        'Status',
        choices=[(s.name, s.value) for s in PuppyStatus],
        coerce=lambda x: PuppyStatus[x] if isinstance(x, str) else x,
        validators=[DataRequired()]
    )

    image_upload = FileField('Upload New Main Image')


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
        choices = []
        for litter in litters:
            mom_name = litter.mother.name if litter.mother else "Unknown Mom"
            dad_name = litter.father.name if litter.father else "Unknown Dad"
            born = litter.birth_date.strftime('%B %Y') if litter.birth_date else "Unknown Date"
            label = f"Litter from {mom_name} & {dad_name} (Born: {born})"
            choices.append((litter.id, label))
        return choices

    def _populate_form_choices(self, form_instance, obj=None):
        """
        Populates the Litter dropdown.
        IMPORTANT: only pre-select the current litter on initial GET.
        Do NOT overwrite on POST, or the user's selection will be lost.
        """
        form_instance.litter_id.choices = self._get_litter_choices()

        # Only set default selection when the form is NOT submitted (GET render)
        if (not form_instance.is_submitted()) and obj and obj.litter_id:
            form_instance.litter_id.data = obj.litter_id

        return form_instance

    def create_form(self):
        form_instance = super().create_form()
        return self._populate_form_choices(form_instance)

    def edit_form(self, obj=None):
        form_instance = super().edit_form(obj)
        return self._populate_form_choices(form_instance, obj)

    def on_model_change(self, form, model, is_created):
        """Handles saving relationships and processing image uploads."""
        model.litter_id = form.litter_id.data

        file = request.files.get('image_upload')
        if file and file.filename:
            s3_key = upload_image(file, folder='puppies')
            if s3_key:
                model.main_image_s3_key = s3_key
