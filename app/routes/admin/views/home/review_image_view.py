# app/routes/admin/views/home/review_image_view.py

from ..base import AdminModelView


class ReviewImageAdminView(AdminModelView):
    """
    Admin view for ReviewImage.

    This view is intentionally hidden from the admin navigation so the dashboard
    remains a single "Reviews" management surface (images are typically added
    via the Review edit page using the file upload field).
    """

    can_create = True
    can_edit = True
    can_delete = True

    # Hide from sidebar/navigation so you don't get a separate "Images" admin page
    def is_visible(self):
        return False

    # Keep it minimal (no caption)
    column_list = ("review", "sort_order", "s3_key")
    form_columns = ("review", "sort_order", "s3_key")