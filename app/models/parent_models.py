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
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    role = db.Column(db.Enum(ParentRole), nullable=False)
    breed = db.Column(db.String(100))
    birth_date = db.Column(db.Date)
    weight_kg = db.Column(db.Float)
    height_cm = db.Column(db.Float)
    description = db.Column(db.Text)
    
    # Flags for managing parent visibility and status
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    is_guardian = db.Column(db.Boolean, default=False, nullable=False)

    # S3 keys for the parent's main image, with responsive sizes.
    main_image_s3_key = db.Column(db.String(255))
    main_image_s3_key_small = db.Column(db.String(255))
    main_image_s3_key_medium = db.Column(db.String(255))
    main_image_s3_key_large = db.Column(db.String(255))

    # S3 keys for additional gallery images.
    alternate_image_s3_key_1 = db.Column(db.String(255))
    alternate_image_s3_key_2 = db.Column(db.String(255))
    alternate_image_s3_key_3 = db.Column(db.String(255))
    alternate_image_s3_key_4 = db.Column(db.String(255))

    # Relationships to the ParentImage model for a flexible gallery.
    images = db.relationship('ParentImage', backref='parent', lazy=True, cascade="all, delete-orphan")

    # UPDATED: Relationships now point to the Litter model instead of Puppy.
    # This matches the new architecture where parents are defined at the Litter level.
    litters_as_dad = db.relationship('Litter', foreign_keys='Litter.dad_id', back_populates='dad', lazy='dynamic')
    litters_as_mom = db.relationship('Litter', foreign_keys='Litter.mom_id', back_populates='mom', lazy='dynamic')

    def __init__(self, **kwargs):
        """
        Explicit constructor to ensure stable object creation.
        """
        super(Parent, self).__init__(**kwargs)

    @property
    def litters(self):
        """
        A convenience property to access the parent's litters based on their role.
        """
        if self.role == ParentRole.DAD:
            return self.litters_as_dad
        else:
            return self.litters_as_mom

    @property
    def grouped_litters(self):
        """
        Returns the parent's litters ordered by birth date (newest first).
        Since we now have a dedicated Litter model, we return the Litter objects directly.
        """
        return self.litters.order_by(db.desc('birth_date')).all()

    def __repr__(self):
        """Provides a developer-friendly representation of the Parent object."""
        return f'<Parent {self.name}>'

    def __str__(self):
        """Provides a user-friendly string representation (the parent's name)."""
        return self.name

class ParentImage(db.Model):
    """
    Represents an individual gallery image associated with a Parent.
    """
    id = db.Column(db.Integer, primary_key=True)
    parent_id = db.Column(db.Integer, db.ForeignKey('parent.id'), nullable=False)
    image_s3_key = db.Column(db.String(255), nullable=False)
    caption = db.Column(db.String(255))

    def __repr__(self):
        """Provides a developer-friendly representation of the ParentImage object."""
        return f'<ParentImage {self.id} for Parent ID {self.parent_id}>'