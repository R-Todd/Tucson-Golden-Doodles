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
    """
    Creates the display label for each Litter in the dropdown.
    Example: "Litter from Penelope & Archie (Born: January 2024)"
    """
    if not litter:
        return "Invalid Litter"

    mom_name = litter.mother.name if litter.mother else "Unknown Mom"
    dad_name = litter.father.name if litter.father else "Unknown Dad"
    born = litter.birth_date.strftime('%B %Y') if litter.birth_date else "Unknown Date"

    return f"Litter from {mom_name} & {dad_name} (Born: {born})"


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
        blank_text='-- Select a Litter --'
    )
