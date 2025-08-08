# app/routes/admin/views/home/review_view.py

from ..base import AdminModelView

class ReviewAdminView(AdminModelView):
    """A custom view for Reviews that uses an organized Bootstrap 5 template."""
    # Point to the new organized template file
    list_template = 'admin/reviews/list_bs5.html'

    # Add other template overrides here for create/edit when you get to them
    # create_template = 'admin/reviews/create_bs5.html'
    # edit_template = 'admin/reviews/edit_bs5.html'