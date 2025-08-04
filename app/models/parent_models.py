# app/models/parent_models.py
"""
Defines the models for parent dogs (Sires and Dams) and their associated images.
"""

from . import db
from .enums import ParentRole
from collections import OrderedDict
from itertools import groupby

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

    # DEPRECATED: Replaced by ParentImage model for a more flexible gallery.
    images = db.relationship('ParentImage', backref='parent', lazy=True, cascade="all, delete-orphan")

    # Relationships to the Puppy model, distinguishing litters by parental role.
    litters_as_dad = db.relationship('Puppy', foreign_keys='Puppy.dad_id', back_populates='dad', lazy='dynamic')
    litters_as_mom = db.relationship('Puppy', foreign_keys='Puppy.mom_id', back_populates='mom', lazy='dynamic')


    def __init__(self, **kwargs):
        """
        Explicit constructor to ensure stable object creation, especially in tests.
        Allows for initializing a Parent instance with keyword arguments.
        """
        super(Parent, self).__init__(**kwargs)

    @property
    def litters(self):
        """
        A convenience property to access the parent's litters, regardless of role.
        Returns `litters_as_dad` or `litters_as_mom` based on the parent's role.
        """
        if self.role == ParentRole.DAD:
            return self.litters_as_dad
        else:
            return self.litters_as_mom

    @property
    def grouped_litters(self):
        """
        Groups a parent's puppies into litters.

        A litter is defined by a unique combination of birth date, mom, and dad.
        Returns an OrderedDict with the litter key (birth_date, dad, mom) and
        a list of puppies in that litter as the value.
        """
        from .puppy_models import Puppy
        puppies = self.litters.order_by(Puppy.birth_date.desc(), Puppy.name).all()
        keyfunc = lambda p: (p.birth_date, p.dad, p.mom)
        return OrderedDict((k, list(g)) for k, g in groupby(puppies, keyfunc))

    def __repr__(self):
        """Provides a developer-friendly representation of the Parent object."""
        return f'<Parent {self.name}>'

    def __str__(self):
        """Provides a user-friendly string representation (the parent's name)."""
        return self.name

class ParentImage(db.Model):
    """
    Represents an individual gallery image associated with a Parent.
    This provides a more flexible one-to-many relationship for parent photos.
    """
    id = db.Column(db.Integer, primary_key=True)
    parent_id = db.Column(db.Integer, db.ForeignKey('parent.id'), nullable=False)
    image_s3_key = db.Column(db.String(255), nullable=False)
    caption = db.Column(db.String(255))

    def __repr__(self):
        """Provides a developer-friendly representation of the ParentImage object."""
        return f'<ParentImage {self.id} for Parent ID {self.parent_id}>'