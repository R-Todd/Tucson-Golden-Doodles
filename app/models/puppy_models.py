from . import db
from .enums import PuppyStatus

# Puppies from litters
class Puppy(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100)) # e.g., "Blue Collar Male"
    birth_date = db.Column(db.Date, nullable=False)
    status = db.Column(db.Enum(PuppyStatus), nullable=False, default=PuppyStatus.AVAILABLE)
    dad_id = db.Column(db.Integer, db.ForeignKey('parent.id'), nullable=False)
    mom_id = db.Column(db.Integer, db.ForeignKey('parent.id'), nullable=False)
    main_image_url = db.Column(db.String(255))

    def __repr__(self):
        return f'<Puppy {self.id} ({self.name})>'