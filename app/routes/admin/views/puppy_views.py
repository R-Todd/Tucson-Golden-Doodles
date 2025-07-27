# app/routes/admin/views/puppy_views.py

from flask import request
from wtforms import Form, StringField, DateField, SelectField, FileField
from wtforms.validators import DataRequired
from flask_admin.contrib.sqla.fields import QuerySelectField
from .base import AdminModelView
from app.models import Parent, ParentRole, PuppyStatus
from app.utils.image_uploader import upload_image

# Define a dedicated form for creating/editing puppies to ensure proper validation
# and to correctly filter the parent selection dropdowns.
class PuppyForm(Form):
    name = StringField('Name', validators=[DataRequired()])
    birth_date = DateField('Birth Date', format='%Y-%m-%d', validators=[DataRequired()])
    # Query factory ensures the 'Mother' dropdown only shows parents with the MOM role.
    mom = QuerySelectField(
        'Mother',
        query_factory=lambda: Parent.query.filter_by(role=ParentRole.MOM).all(),
        get_label='name',
        allow_blank=False,
        validators=[DataRequired()]
    )
    # Query factory ensures the 'Father' dropdown only shows parents with the DAD role.
    dad = QuerySelectField(
        'Father',
        query_factory=lambda: Parent.query.filter_by(role=ParentRole.DAD).all(),
        get_label='name',
        allow_blank=False,
        validators=[DataRequired()]
    )
    status = SelectField(
        'Status',
        choices=[(s.name, s.value) for s in PuppyStatus],
        coerce=lambda x: PuppyStatus[x] if isinstance(x, str) else x,
        validators=[DataRequired()]
    )
    # This is the field for uploading a new image.
    image_upload = FileField('Upload New Main Image')

class PuppyAdminView(AdminModelView):
    """ Custom Admin view for managing Puppies. """
    # Use the custom form defined above for create and edit pages.
    form = PuppyForm
    # Explicitly list the columns to display in the form.
    form_columns = ['name', 'birth_date', 'status', 'mom', 'dad', 'image_upload']

    # This method adds the data for the current image thumbnail preview.
    def edit_form(self, obj=None):
        form = super(PuppyAdminView, self).edit_form(obj)
        if obj and obj.main_image_url:
            if form.image_upload.render_kw is None:
                form.image_upload.render_kw = {}
            form.image_upload.render_kw['data-current-image'] = obj.main_image_url
        return form

    # This method handles the file upload when the form is saved.
    def on_model_change(self, form, model, is_created):
        file = request.files.get('image_upload')
        if file and file.filename:
            # Upload the image to S3 and save the URL.
            # Responsive versions are not created for individual puppy images by default.
            image_url = upload_image(file, folder='puppies')
            if image_url:
                model.main_image_url = image_url