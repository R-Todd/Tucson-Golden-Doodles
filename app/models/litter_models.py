# app/models/litter_models.py
from . import db
from datetime import date

class Litter(db.Model):
    """
    Represents a group of puppies born from the same parents at the same time.
    Shared traits like breed, expected size, and parents are stored here.
    """
    id = db.Column(db.Integer, primary_key=True)
    birth_date = db.Column(db.Date, nullable=False, default=date.today)
    
    # Shared physical traits for the entire litter
    breed = db.Column(db.String(100), nullable=False) # e.g., F1b Goldendoodle
    expected_size = db.Column(db.String(100))        # e.g., 20-30 lbs
    
    # Parental links moved from Puppy to Litter
    dad_id = db.Column(db.Integer, db.ForeignKey('parent.id'), nullable=False)
    mom_id = db.Column(db.Integer, db.ForeignKey('parent.id'), nullable=False)
    
    # Relationships
    mom = db.relationship('Parent', foreign_keys=[mom_id])
    dad = db.relationship('Parent', foreign_keys=[dad_id])
    
    # Link to puppies in this litter
    puppies = db.relationship('Puppy', back_populates='litter', cascade="all, delete-orphan")

    def __repr__(self):
        return f'<Litter {self.id} - {self.mom.name} x {self.dad.name} ({self.birth_date})>'