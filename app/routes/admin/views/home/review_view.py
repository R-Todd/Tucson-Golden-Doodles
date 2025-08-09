# app/routes/admin/views/home/review_view.py

from ..base import AdminModelView
from flask import request

class ReviewAdminView(AdminModelView):
    """A custom view for Reviews that uses an organized Bootstrap 5 template."""
    list_template = 'admin/reviews/list_bs5.html'
    create_template = 'admin/reviews/create_bs5.html'
    edit_template = 'admin/reviews/edit_bs5.html'

    # --- ADD THESE LINES ---
    # Specify columns to display in the list view
    column_list = ('author_name', 'is_featured', 'testimonial_text')

    # Specify the fields to include in the create and edit forms
    form_columns = ('author_name', 'testimonial_text', 'is_featured')

    # Make the text area larger for a better editing experience
    form_widget_args = {
        'testimonial_text': {
            'rows': 10
        }
    }
    # --- END OF ADDED LINES ---

    def on_model_change(self, form, model, is_created):
        """
        This function is called when a review is created or updated.
        """
        pass