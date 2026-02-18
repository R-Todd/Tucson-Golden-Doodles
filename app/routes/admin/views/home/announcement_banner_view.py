# app/routes/admin/views/home/announcement_banner_view.py

import json
from ..base import AdminModelView
from app.routes.admin.forms.announcement_forms import AnnouncementBannerForm
from app.models import Litter


class AnnouncementBannerAdminView(AdminModelView):
    """
    Custom Admin View for the Announcement Banner.
    Now fully Litter-based (no more Puppy grouping).
    """

    can_create = True
    can_edit = True
    can_delete = True

    list_template = 'admin/announcement_banner/list_bs5.html'
    create_template = 'admin/announcement_banner/create_bs5.html'
    edit_template = 'admin/announcement_banner/edit_bs5.html'

    form = AnnouncementBannerForm
    column_list = ('is_active', 'main_text', 'featured_puppy')

    form_widget_args = {
        'main_text': {'id': 'main_text'},
        'sub_text': {'id': 'sub_text'},
        'button_text': {'id': 'button_text'},
        'featured_puppy': {'id': 'featured_puppy'}
    }

    def _get_template_args(self):
        """
        Injects JSON-serialized Litter data for the preview JavaScript.
        """
        args = super()._get_template_args()

        litters = Litter.query.order_by(Litter.birth_date.desc()).all()

        litters_for_json = [
            {
                "id": litter.id,
                "mom_name": litter.mother.name if litter.mother else "Unknown Mom",
                "dad_name": litter.father.name if litter.father else "Unknown Dad",
                "birth_date": litter.birth_date.strftime("%B %d, %Y") if litter.birth_date else ""
            }
            for litter in litters
        ]

        args['litters_json'] = json.dumps(litters_for_json)
        return args

    def on_model_change(self, form, model, is_created):
        """
        Store the selected Litter ID in the featured_puppy field.
        (Field name remains for backward compatibility.)
        """
        selected_litter = form.featured_puppy.data

        if selected_litter:
            model.featured_puppy_id = selected_litter.id
        else:
            model.featured_puppy_id = None
