# app/models/puppy_models.py
"""
Defines the Puppy model, which is central to tracking individual puppies.
"""

from . import db
from .enums import PuppyStatus
from .parent_models import Parent

class Puppy(db.Model):
    """
    Represents an individual puppy.

    This model stores information about each puppy, including its name, birth date,
    status, and its parentage through relationships with the Parent model.
    """
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    birth_date = db.Column(db.Date, nullable=False)
    status = db.Column(db.Enum(PuppyStatus), nullable=False, default=PuppyStatus.AVAILABLE)

    # --- BREED RELATIONSHIP ---
    # This is the foreign key that links a puppy to a specific breed.
    breed_id = db.Column(db.Integer, db.ForeignKey('breed.id'), nullable=True)
    # This creates the relationship, allowing you to access the Breed object.
    breed = db.relationship('Breed', backref='puppies')

    # Foreign keys linking the puppy to its parents in the 'parent' table.
    dad_id = db.Column(db.Integer, db.ForeignKey('parent.id'), nullable=False)
    mom_id = db.Column(db.Integer, db.ForeignKey('parent.id'), nullable=False)
    
    # S3 key for the puppy's main profile image.
    main_image_s3_key = db.Column(db.String(255))

    # Relationships to the Parent model to easily access mom and dad objects.
    mom = db.relationship('Parent', foreign_keys=[mom_id], back_populates='litters_as_mom')
    dad = db.relationship('Parent', foreign_keys=[dad_id], back_populates='litters_as_dad')

    def __repr__(self):
        """Provides a developer-friendly representation of the Puppy object."""
        return f'<Puppy {self.id} ({self.name})>'