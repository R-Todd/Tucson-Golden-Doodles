# app/routes/admin/views/parent_views.py

from flask import request
from .base import AdminModelView
from app.utils.image_uploader import upload_image
from ..forms import ParentForm # Import the new ParentForm

class ParentAdminView(AdminModelView):
    edit_template = 'admin/parent_edit.html'
    create_template = 'admin/parent_edit.html'
    column_list = ['name', 'role', 'breed', 'is_active', 'is_guardian']
    form = ParentForm

    # --- NEW: Add a debug print statement to the edit_form method ---
    def edit_form(self, obj=None):
        # This method is called by Flask-Admin to get the form for the edit page.
        # We will get the form from the parent class first.
        form = super(ParentAdminView, self).edit_form(obj)
        
        # --- DEBUGGING ---
        # Let's print the form object and its fields to the console.
        print("\n" + "="*50)
        print("DEBUG: Inside ParentAdminView.edit_form")
        print(f"Is form object valid? {form is not None}")
        if form:
            print(f"Form object type: {type(form)}")
            # The _fields attribute is a dictionary of all fields in the form.
            print(f"Fields available in form: {list(form._fields.keys())}")
        print("="*50 + "\n")
        # --- END DEBUGGING ---

        return form

    def on_model_change(self, form, model, is_created):
        """Handle image uploads when a parent record is saved."""
        main_file = request.files.get('image_upload')
        if main_file and main_file.filename:
            image_urls = upload_image(main_file, folder='parents', create_responsive_versions=True)
            if image_urls:
                model.main_image_url = image_urls.get('original')
                model.main_image_url_small = image_urls.get('small')
                model.main_image_url_medium = image_urls.get('medium')
                model.main_image_url_large = image_urls.get('large')

        alt_fields = [
            'alternate_image_upload_1', 'alternate_image_upload_2',
            'alternate_image_upload_3', 'alternate_image_upload_4'
        ]
        alt_model_attrs = [
            'alternate_image_url_1', 'alternate_image_url_2',
            'alternate_image_url_3', 'alternate_image_url_4'
        ]

        for i, field_name in enumerate(alt_fields):
            file = request.files.get(field_name)
            if file and file.filename:
                url = upload_image(file, folder='parents_alternates')
                if url:
                    setattr(model, alt_model_attrs[i], url)