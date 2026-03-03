from . import db
from datetime import date
from .enums import PuppyStatus


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
    birth_date = db.Column(db.Date, nullable=False)
    breed_name = db.Column(db.String(120), nullable=True)
    description = db.Column(db.Text, nullable=True)
    expected_weight = db.Column(db.String(120), nullable=True)

    # Litter status override:
    # - "auto" (default): past if there are ZERO available puppies
    # - "force_past": always treat as past (hides from Current Litters)
    status_mode = db.Column(db.String(20), default="auto", nullable=False, index=True)

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
    def is_past(self) -> bool:
        """Return True if this litter should be treated as a past litter.

        Rules (Auto is always on):
        - Admin override: status_mode == "force_past" => past
        - Otherwise: past if there are ZERO available puppies
        """
        mode = (self.status_mode or "auto").strip().lower()
        if mode == "force_past":
            return True

        # Auto: past if no puppies are AVAILABLE
        if not self.puppies:
            return True

        return not any(p.status == PuppyStatus.AVAILABLE for p in self.puppies)

    def __str__(self):
        # Helps Flask-Admin / WTForms render this object consistently.
        return self.display_label

    def __repr__(self):
        return f"<Litter {self.id} - {self.breed_name or 'Unnamed'}>"