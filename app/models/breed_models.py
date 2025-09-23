# app/models/breed_model.py
"""
Defines the Breed model for storing a list of dog breeds.
"""

from . import db

class Breed(db.Model):
    """
    Represents a dog breed.
    """
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)

    def __repr__(self):
        """Provides a developer-friendly representation of the Breed object."""
        return f'<Breed {self.name}>'