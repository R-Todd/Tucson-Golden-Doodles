# app/models/parent_models.py

from . import db
from .enums import ParentRole
from collections import OrderedDict
from itertools import groupby

# Parent dogs (Sires and Dams)
class Parent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    role = db.Column(db.Enum(ParentRole), nullable=False)
    breed = db.Column(db.String(100))
    birth_date = db.Column(db.Date)
    weight_kg = db.Column(db.Float)
    height_cm = db.Column(db.Float)
    description = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    is_guardian = db.Column(db.Boolean, default=False, nullable=False)

    # --- RENAMED FIELDS for S3 Keys ---
    main_image_s3_key = db.Column(db.String(255))
    main_image_s3_key_small = db.Column(db.String(255))
    main_image_s3_key_medium = db.Column(db.String(255))
    main_image_s3_key_large = db.Column(db.String(255))
    alternate_image_s3_key_1 = db.Column(db.String(255))
    alternate_image_s3_key_2 = db.Column(db.String(255))
    alternate_image_s3_key_3 = db.Column(db.String(255))
    alternate_image_s3_key_4 = db.Column(db.String(255))

    # One-to-many relationship to ParentImage
    images = db.relationship('ParentImage', backref='parent', lazy=True, cascade="all, delete-orphan")

    # Relationships to Puppy, distinguishing between dad and mom roles
    litters_as_dad = db.relationship('Puppy', foreign_keys='Puppy.dad_id', back_populates='dad', lazy='dynamic')
    litters_as_mom = db.relationship('Puppy', foreign_keys='Puppy.mom_id', back_populates='mom', lazy='dynamic')

    # --- THIS IS THE FIX ---
    # Add an explicit constructor to ensure stable object creation in tests.
    def __init__(self, **kwargs):
        super(Parent, self).__init__(**kwargs)

    @property
    def litters(self):
        """Returns a query for all puppies from this parent, based on role."""
        if self.role == ParentRole.DAD:
            return self.litters_as_dad
        else:
            return self.litters_as_mom

    @property
    def grouped_litters(self):
        """Groups this parent's puppies by litter, ordered by date."""
        from .puppy_models import Puppy # Local import to prevent circular dependency
        puppies = self.litters.order_by(Puppy.birth_date.desc(), Puppy.name).all()
        keyfunc = lambda p: (p.birth_date, p.dad, p.mom)
        return OrderedDict((k, list(g)) for k, g in groupby(puppies, keyfunc))

    def __repr__(self):
        return f'<Parent {self.name}>'

    def __str__(self):
        return self.name

# Gallery images for parents
class ParentImage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    parent_id = db.Column(db.Integer, db.ForeignKey('parent.id'), nullable=False)
    image_s3_key = db.Column(db.String(255), nullable=False) # Renamed field
    caption = db.Column(db.String(255))

    def __repr__(self):
        return f'<ParentImage {self.id} for Parent {self.parent_id}>'