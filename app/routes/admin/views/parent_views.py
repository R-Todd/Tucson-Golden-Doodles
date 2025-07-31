# app/routes/admin/views/parent_views.py

from flask import request
from .base import AdminModelView
from app.utils.image_uploader import upload_image
from ..forms import ParentForm 

class ParentAdminView(AdminModelView):
    edit_template = 'admin/parent_edit.html'
    create_template = 'admin/parent_edit.html'
    column_list = ['name', 'role', 'breed', 'is_active', 'is_guardian']
    form = ParentForm

    def edit_form(self, obj=None):
        form = super(ParentAdminView, self).edit_form(obj)
        
        # --- DEBUGGING & LOGIC FOR MAIN IMAGE ---
        print("\n" + "="*50)
        print("DEBUG: Preparing form for the template.")
        
        if obj and obj.main_image_url:
            print(f"Found main_image_url: {obj.main_image_url}")
            if hasattr(form, 'image_upload'):
                if form.image_upload.render_kw is None:
                    form.image_upload.render_kw = {}
                # This adds the URL for our JavaScript to find
                form.image_upload.render_kw['data-current-image'] = obj.main_image_url
                print("Successfully added 'data-current-image' to the form field.")
        else:
            print("No existing main image found for this parent.")
            
        print("="*50 + "\n")
        return form

    def on_model_change(self, form, model, is_created):
        # Temporarily disabled to focus on displaying the image.
        pass