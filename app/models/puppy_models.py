# app/models/puppy_models.py
"""
Defines the Puppy model, which represents individual puppies
belonging to a specific litter.
"""

from . import db
from .enums import PuppyStatus


class Puppy(db.Model):
    """
    Represents an individual puppy.

    A puppy now belongs to a Litter.
    Parent relationships and birth date are inherited
    through the litter.
    """

    __tablename__ = "puppy"

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(100), nullable=False)

    # NEW: Puppy-specific field
    coat = db.Column(db.String(100), nullable=True)

    status = db.Column(
        db.Enum(PuppyStatus),
        nullable=False,
        default=PuppyStatus.AVAILABLE
    )

    # NEW: Relationship to Litter
    litter_id = db.Column(
        db.Integer,
        db.ForeignKey("litter.id"),
        nullable=False
    )

    # Puppy image
    main_image_s3_key = db.Column(db.String(255))

    def __repr__(self):
        return f"<Puppy {self.id} ({self.name})>"
