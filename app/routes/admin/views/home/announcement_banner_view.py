# app/routes/admin/views/home/announcement_banner_view.py

import json
from ..base import AdminModelView
# This import is updated to point to the new dedicated form file
from app.routes.admin.forms.announcement_forms import AnnouncementBannerForm, get_litters 

class AnnouncementBannerAdminView(AdminModelView):
    """
    Custom Admin View for the Announcement Banner, now using isolated Bootstrap 5 templates.
    """
    can_create = True
    can_edit = True
    can_delete = True

    list_template = 'admin/announcement_banner/list_bs5.html'
    create_template = 'admin/announcement_banner/create_bs5.html'
    edit_template = 'admin/announcement_banner/edit_bs5.html'

    # The form is now imported from its new location
    form = AnnouncementBannerForm 
    column_list = ('is_active', 'main_text', 'featured_puppy')

    form_widget_args = {
        'main_text': { 'id': 'main_text' },
        'sub_text': { 'id': 'sub_text' },
        'button_text': { 'id': 'button_text' },
        'featured_puppy': { 'id': 'featured_puppy' }
    }

    def _get_template_args(self):
        """
        Injects a JSON-serialized list of litters into the template context.
        This provides a clean data source for the preview JavaScript.
        """
        args = super()._get_template_args()
        litters_raw = get_litters()
        
        # Serialize the necessary data into a list of dictionaries
        litters_for_json = [
            {
                "id": puppy.id,
                "mom_name": puppy.mom.name,
                "dad_name": puppy.dad.name,
                "birth_date": puppy.birth_date.strftime("%B %d, %Y")
            }
            for puppy in litters_raw
        ]
        
        args['litters_json'] = json.dumps(litters_for_json)
        return args

    def on_model_change(self, form, model, is_created):
        selected_puppy = form.featured_puppy.data
        if selected_puppy:
            model.featured_puppy_id = selected_puppy.id
        else:
            model.featured_puppy_id = None