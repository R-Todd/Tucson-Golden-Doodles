# app/routes/admin/views/puppy_views.py

from flask import request
from flask_wtf import FlaskForm
from wtforms.fields import FileField, SelectField, DateField, StringField
from wtforms.validators import InputRequired, DataRequired
from .base import AdminModelView
from app.models import Parent, ParentRole, PuppyStatus, db # Import db to query for Parent objects
from app.utils.image_uploader import upload_image

class PuppyForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    birth_date = DateField('Birth Date', validators=[DataRequired()])
    status = SelectField(
        'Status',
        choices=[(s.name, s.value) for s in PuppyStatus],
        coerce=lambda x: PuppyStatus[x] if isinstance(x, str) else x,
        validators=[DataRequired()]
    )
    # Field names correctly match the foreign key columns directly
    mom_id = SelectField( # Changed from 'mom' to 'mom_id'
        'Mother',
        coerce=int,
        validators=[InputRequired(message="Please select a mother.")]
    )
    dad_id = SelectField( # Changed from 'dad' to 'dad_id'
        'Father',
        coerce=int,
        validators=[InputRequired(message="Please select a father.")]
    )
    image_upload = FileField('Upload New Main Image')


class PuppyAdminView(AdminModelView):
    """ Custom Admin view for managing Puppies using a custom form. """

    column_list = ('name', 'mom', 'dad', 'birth_date', 'status')
    form = PuppyForm
    
    def _get_parent_choices(self, role):
        """Helper method to get parents for dropdowns."""
        return [(p.id, p.name) for p in Parent.query.filter_by(role=role).order_by(Parent.name).all()]

    def _populate_form_choices(self, form_instance, obj=None):
        """A helper to populate choices for our 'mom_id' and 'dad_id' fields."""
        form_instance.mom_id.choices = self._get_parent_choices(ParentRole.MOM)
        form_instance.dad_id.choices = self._get_parent_choices(ParentRole.DAD)
        if obj:
            form_instance.mom_id.data = obj.mom_id
            form_instance.dad_id.data = obj.dad_id
        return form_instance

    def create_form(self):
        """Override to populate choices when creating a new puppy."""
        form_instance = super().create_form()
        return self._populate_form_choices(form_instance)

    def edit_form(self, obj=None):
        """Override to populate choices and set defaults when editing a puppy."""
        form_instance = super().edit_form(obj)
        form_instance = self._populate_form_choices(form_instance, obj)
        
        if obj and obj.main_image_url:
            if form_instance.image_upload.render_kw is None:
                form_instance.image_upload.render_kw = {}
            form_instance.image_upload.render_kw['data-current-image'] = obj.main_image_url
        return form_instance

    def on_model_change(self, form, model, is_created):
        """
        Manually fetch the Parent objects and assign them to the relationship properties.
        This ensures SQLAlchemy correctly handles the relationships and back-population.
        """
        # Fetch Parent objects based on the IDs from the form
        mom_obj = db.session.get(Parent, form.mom_id.data)
        dad_obj = db.session.get(Parent, form.dad_id.data)

        # Assign the Parent objects to the relationship attributes
        model.mom = mom_obj
        model.dad = dad_obj
        
        # Flask-Admin's populate_obj will also set mom_id and dad_id columns correctly
        # because the form field names match the model's foreign key column names.
        # So we don't need to explicitly do:
        # model.mom_id = form.mom_id.data
        # model.dad_id = form.dad_id.data
        
        file = request.files.get('image_upload')
        if file and file.filename:
            image_url = upload_image(file, folder='puppies')
            if image_url:
                model.main_image_url = image_url