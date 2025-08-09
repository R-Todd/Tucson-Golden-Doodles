# app/routes/admin/views/home/review_view.py

from ..base import AdminModelView
from flask import request

class ReviewAdminView(AdminModelView):
    """A custom view for Reviews that uses an organized Bootstrap 5 template."""
    list_template = 'admin/reviews/list_bs5.html'
    create_template = 'admin/reviews/create_bs5.html'
    edit_template = 'admin/reviews/edit_bs5.html'

    # Add the on_model_change method to handle form submissions
    def on_model_change(self, form, model, is_created):
        """
        This function is called when a review is created or updated.
        """
        # No special logic is needed for reviews, but this method ensures
        # that the form data is correctly processed and saved.
        pass