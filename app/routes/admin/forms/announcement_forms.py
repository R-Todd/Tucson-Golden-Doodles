# app/routes/admin/forms/announcement_forms.py

from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField
from wtforms.validators import DataRequired
from wtforms_sqlalchemy.fields import QuerySelectField

from app.models import Litter


def get_litters():
    """
    Returns all litters for the dropdown, newest first.
    """
    return (
        Litter.query
        .order_by(Litter.birth_date.desc())
        .all()
    )


def get_litter_label(litter):
    """Returns the standardized label used everywhere."""
    return litter.display_label if litter else "Invalid Litter"


class AnnouncementBannerForm(FlaskForm):
    """Custom form for the Announcement Banner admin view."""
    is_active = BooleanField('Is Active', default=True)
    main_text = StringField('Main Text', validators=[DataRequired()])

    sub_text = StringField(
        'Sub Text',
        validators=[DataRequired()],
        description="Use placeholders: {mom_name}, {dad_name}, {birth_date}"
    )

    button_text = StringField('Button Text', validators=[DataRequired()])

    # NOTE: Field name kept as 'featured_puppy' for compatibility with existing templates/JS.
    # It will now return a Litter object.
    featured_puppy = QuerySelectField(
        'Featured Litter',
        query_factory=get_litters,
        get_label=get_litter_label,
        allow_blank=True,
        blank_text='-- None --'
    )
