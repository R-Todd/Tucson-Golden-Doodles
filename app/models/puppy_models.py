from . import db
from .enums import PuppyStatus
# Import the Parent model to define the relationship
from .parent_models import Parent

# Puppies from litters
class Puppy(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False) # e.g., "Blue Collar Male"
    birth_date = db.Column(db.Date, nullable=False)
    status = db.Column(db.Enum(PuppyStatus), nullable=False, default=PuppyStatus.AVAILABLE)
    dad_id = db.Column(db.Integer, db.ForeignKey('parent.id'), nullable=False)
    mom_id = db.Column(db.Integer, db.ForeignKey('parent.id'), nullable=False)
    main_image_url = db.Column(db.String(255))

    
    # Explicitly define the relationships to the Parent model.
    # This makes them discoverable by Flask-Admin during startup.
    mom = db.relationship('Parent', foreign_keys=[mom_id], back_populates='litters_as_mom')
    dad = db.relationship('Parent', foreign_keys=[dad_id], back_populates='litters_as_dad')


    def __repr__(self):
        return f'<Puppy {self.id} ({self.name})>'