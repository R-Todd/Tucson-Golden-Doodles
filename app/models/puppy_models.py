# app/models/puppy_models.py
from . import db
from .enums import PuppyStatus

class Puppy(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    status = db.Column(db.Enum(PuppyStatus), nullable=False, default=PuppyStatus.AVAILABLE)
    gender = db.Column(db.String(10)) # Added for individual puppy detail
    
    # Individual override fields (optional)
    coat_color = db.Column(db.String(100)) 
    
    # Link to the Litter
    litter_id = db.Column(db.Integer, db.ForeignKey('litter.id'), nullable=False)
    litter = db.relationship('Litter', back_populates='puppies')
    
    main_image_s3_key = db.Column(db.String(255))

    def __repr__(self):
        return f'<Puppy {self.name} (Litter {self.litter_id})>'