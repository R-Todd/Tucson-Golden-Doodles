# app/models/parent_models.py
"""
Defines the models for parent dogs (Sires and Dams) and their associated images.
"""

from . import db
from .enums import ParentRole


class Parent(db.Model):
    """
    Represents a parent dog (a Sire or a Dam).

    This model stores detailed information about each parent, including their
    role, physical attributes, and relationships to litters of puppies.
    """

    __tablename__ = "parent"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    role = db.Column(db.Enum(ParentRole), nullable=False)
    breed = db.Column(db.String(100))
    birth_date = db.Column(db.Date)
    weight_kg = db.Column(db.Float)
    height_cm = db.Column(db.Float)
    description = db.Column(db.Text)

    # Visibility flags
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    is_guardian = db.Column(db.Boolean, default=False, nullable=False)

    # Main image (responsive versions)
    main_image_s3_key = db.Column(db.String(255))
    main_image_s3_key_small = db.Column(db.String(255))
    main_image_s3_key_medium = db.Column(db.String(255))
    main_image_s3_key_large = db.Column(db.String(255))

    # Optional alternate images
    alternate_image_s3_key_1 = db.Column(db.String(255))
    alternate_image_s3_key_2 = db.Column(db.String(255))
    alternate_image_s3_key_3 = db.Column(db.String(255))
    alternate_image_s3_key_4 = db.Column(db.String(255))

    # Flexible image gallery
    images = db.relationship(
        "ParentImage",
        backref="parent",
        lazy=True,
        cascade="all, delete-orphan"
    )

    # ✅ NEW: Relationship to Litter model
    litters_as_mom = db.relationship(
        "Litter",
        foreign_keys="Litter.mom_id",
        backref="mother",
        lazy=True,
        cascade="all, delete-orphan"
    )

    litters_as_dad = db.relationship(
        "Litter",
        foreign_keys="Litter.dad_id",
        backref="father",
        lazy=True,
        cascade="all, delete-orphan"
    )

    @property
    def litters(self):
        """
        Convenience property to return all litters for this parent,
        based on their role.
        """
        if self.role == ParentRole.DAD:
            return self.litters_as_dad
        return self.litters_as_mom

    def __repr__(self):
        return f"<Parent {self.name}>"

    def __str__(self):
        return self.name


class ParentImage(db.Model):
    """
    Represents an individual gallery image associated with a Parent.
    """

    __tablename__ = "parent_image"

    id = db.Column(db.Integer, primary_key=True)
    parent_id = db.Column(db.Integer, db.ForeignKey("parent.id"), nullable=False)
    image_s3_key = db.Column(db.String(255), nullable=False)
    caption = db.Column(db.String(255))

    def __repr__(self):
        return f"<ParentImage {self.id} for Parent ID {self.parent_id}>"
