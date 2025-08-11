# app/routes/admin/views/home/review_view.py

from ..base import AdminModelView
from flask import request

class ReviewAdminView(AdminModelView):
    """A custom view for Reviews that uses an organized Bootstrap 5 template."""
    
    can_create = True
    can_edit = True
    can_delete = True

    # Template configuration
    list_template = 'admin/reviews/list_bs5.html'
    create_template = 'admin/reviews/create_bs5.html'
    edit_template = 'admin/reviews/edit_bs5.html'

    # Specify columns to display in the list view
    column_list = ('author_name', 'is_featured', 'testimonial_text')

    # Specify the fields to include in the create and edit forms
    form_columns = ('author_name', 'testimonial_text', 'is_featured')

    # --- THIS IS THE FIX ---
    # Add IDs to the form widgets so the preview JavaScript can find them.
    form_widget_args = {
        'author_name': {
            'id': 'author_name'
        },
        'testimonial_text': {
            'id': 'testimonial_text',
            'rows': 10
        }
    }
    # --- END OF FIX ---