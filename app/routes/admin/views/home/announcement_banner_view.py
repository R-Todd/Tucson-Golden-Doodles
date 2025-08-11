# app/routes/admin/views/home/announcement_banner_view.py

from ..base import AdminModelView
from ...forms import AnnouncementBannerForm

class AnnouncementBannerAdminView(AdminModelView):
    """
    Custom Admin View for the Announcement Banner, now using isolated Bootstrap 5 templates.
    """
    # --- Action Buttons ---
    can_create = True
    can_edit = True
    can_delete = True

    # --- Template Configuration ---
    # Point the view to the new, dedicated BS5 templates.
    list_template = 'admin/announcement_banner/list_bs5.html'
    create_template = 'admin/announcement_banner/create_bs5.html'
    edit_template = 'admin/announcement_banner/edit_bs5.html'

    # --- Form & Column Configuration ---
    # Use the custom form that includes the litter selection dropdown.
    form = AnnouncementBannerForm
    # Define the columns to display in the list view for quick reference.
    column_list = ('is_active', 'main_text', 'featured_puppy')

    # Add IDs to the form fields for the live preview JavaScript to target.
    form_widget_args = {
        'main_text': { 'id': 'main_text' },
        'sub_text': { 'id': 'sub_text' },
        'button_text': { 'id': 'button_text' },
        'featured_puppy': { 'id': 'featured_puppy' }
    }

    def on_model_change(self, form, model, is_created):
        """
        Handles saving the featured_puppy relationship from the form.
        """
        selected_puppy = form.featured_puppy.data
        if selected_puppy:
            # A representative puppy from the litter was selected, save its ID.
            model.featured_puppy_id = selected_puppy.id
        else:
            # No litter was selected.
            model.featured_puppy_id = None