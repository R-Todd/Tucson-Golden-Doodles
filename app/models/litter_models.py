from . import db
from datetime import timedelta


class Litter(db.Model):
    """
    Represents a breeding pairing (Mom + Dad) and shared litter metadata.
    Each puppy belongs to exactly one litter.
    """

    __tablename__ = "litter"

    id = db.Column(db.Integer, primary_key=True)

    # Parent relationships
    mom_id = db.Column(db.Integer, db.ForeignKey("parent.id"), nullable=False)
    dad_id = db.Column(db.Integer, db.ForeignKey("parent.id"), nullable=False)

    # Shared litter information
    expected_birth_date = db.Column(db.Date, nullable=True)
    birth_date = db.Column(db.Date, nullable=True)
    breed_name = db.Column(db.String(120), nullable=True)
    description = db.Column(db.Text, nullable=True)
    expected_weight = db.Column(db.String(120), nullable=True)

    # Litter lifecycle stage:
    # - "upcoming": announced pairing / expected litter
    # - "current": active litter shown on the site
    # - "past": archived litter hidden from active pages
    status_mode = db.Column(db.String(20), default="upcoming", nullable=False, index=True)

    # Litter cover image (used on Current Litters page)
    main_image_s3_key = db.Column(db.String(255))

    # Relationship to puppies
    puppies = db.relationship(
        "Puppy",
        backref="litter",
        lazy=True,
        cascade="all, delete-orphan"
    )

    @property
    def display_label(self):
        """
        Standardized one-line label for this litter, used across admin + UI.

        Example:
        "Litter from Penelope & Archie (Born: January 15, 2024)"
        """
        mom_name = self.mother.name if getattr(self, "mother", None) else "Unknown Mom"
        dad_name = self.father.name if getattr(self, "father", None) else "Unknown Dad"
        # born = self.birth_date.strftime("%B %d, %Y") if self.birth_date else "Unknown Date"
        return f"Litter from {mom_name} & {dad_name}"

    @property
    def is_upcoming(self) -> bool:
        """Return True when this litter is configured as upcoming."""
        return (self.status_mode or "upcoming").strip().lower() == "upcoming"

    @property
    def is_past(self) -> bool:
        """Return True when this litter is explicitly configured as past.

        Litter stage is admin-controlled and should not be inferred from
        puppy availability.
        """
        return (self.status_mode or "upcoming").strip().lower() == "past"

    @property
    def take_home_date(self):
        """Return the take-home date, calculated as 8 weeks after birth.

        Uses the actual birth date when available, and falls back to the
        expected birth date for upcoming litters.
        """
        base_date = self.birth_date or self.expected_birth_date
        if not base_date:
            return None
        return base_date + timedelta(weeks=8)

    @property
    def is_current(self) -> bool:
        """Return True when this litter is explicitly configured as current."""
        return (self.status_mode or "upcoming").strip().lower() == "current"

    def __str__(self):
        # Helps Flask-Admin / WTForms render this object consistently.
        return self.display_label

    def __repr__(self):
        return f"<Litter {self.id} - {self.breed_name or 'Unnamed'}>"