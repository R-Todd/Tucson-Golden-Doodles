# app/routes/admin/views/puppy_views.py

from flask import request
from flask_wtf import FlaskForm
from wtforms.fields import FileField, SelectField, DateField, StringField
from wtforms.validators import InputRequired, DataRequired
from .base import AdminModelView
from app.models import Parent, ParentRole, PuppyStatus, db
# --- MODIFIED: Import generate_presigned_url ---
from app.utils.image_uploader import upload_image, generate_presigned_url

class PuppyForm(FlaskForm):
    # --- Form definition remains unchanged ---
    name = StringField('Name', validators=[DataRequired()])
    birth_date = DateField('Birth Date', validators=[DataRequired()])
    status = SelectField(
        'Status',
        choices=[(s.name, s.value) for s in PuppyStatus],
        coerce=lambda x: PuppyStatus[x] if isinstance(x, str) else x,
        validators=[DataRequired()]
    )
    mom_id = SelectField('Mother', coerce=int, validators=[InputRequired(message="Please select a mother.")])
    dad_id = SelectField('Father', coerce=int, validators=[InputRequired(message="Please select a father.")])
    image_upload = FileField('Upload New Main Image')


class PuppyAdminView(AdminModelView):
    """ Custom Admin view for managing Puppies using a custom form. """

    column_list = ('name', 'mom', 'dad', 'birth_date', 'status')
    form = PuppyForm
    
    # --- Helper methods _get_parent_choices and _populate_form_choices remain unchanged ---
    def _get_parent_choices(self, role):
        return [(p.id, p.name) for p in Parent.query.filter_by(role=role).order_by(Parent.name).all()]

    def _populate_form_choices(self, form_instance, obj=None):
        form_instance.mom_id.choices = self._get_parent_choices(ParentRole.MOM)
        form_instance.dad_id.choices = self._get_parent_choices(ParentRole.DAD)
        if obj:
            form_instance.mom_id.data = obj.mom_id
            form_instance.dad_id.data = obj.dad_id
        return form_instance
    
    def create_form(self):
        form_instance = super().create_form()
        return self._populate_form_choices(form_instance)

    def edit_form(self, obj=None):
        """Override to populate choices and set defaults when editing a puppy."""
        form_instance = super().edit_form(obj)
        form_instance = self._populate_form_choices(form_instance, obj)
        
        # --- MODIFIED: Generate pre-signed URL for image preview ---
        if obj and obj.main_image_s3_key:
            if form_instance.image_upload.render_kw is None:
                form_instance.image_upload.render_kw = {}
            form_instance.image_upload.render_kw['data-current-image'] = generate_presigned_url(obj.main_image_s3_key)
        return form_instance

    def on_model_change(self, form, model, is_created):
        """Manually handle relationship assignment and S3 key storage."""
        model.mom = db.session.get(Parent, form.mom_id.data)
        model.dad = db.session.get(Parent, form.dad_id.data)
        
        file = request.files.get('image_upload')
        if file and file.filename:
            # --- MODIFIED: Save the returned S3 key ---
            s3_key = upload_image(file, folder='puppies')
            if s3_key:
                model.main_image_s3_key = s3_key