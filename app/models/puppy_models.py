# app/models/puppy_models.py
from . import db
from .enums import PuppyStatus
from .parent_models import Parent

class Puppy(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    birth_date = db.Column(db.Date, nullable=False)
    status = db.Column(db.Enum(PuppyStatus), nullable=False, default=PuppyStatus.AVAILABLE)
    dad_id = db.Column(db.Integer, db.ForeignKey('parent.id'), nullable=False)
    mom_id = db.Column(db.Integer, db.ForeignKey('parent.id'), nullable=False)
    
    # --- RENAMED FIELD -private s3 ---
    main_image_s3_key = db.Column(db.String(255))

    mom = db.relationship('Parent', foreign_keys=[mom_id], back_populates='litters_as_mom')
    dad = db.relationship('Parent', foreign_keys=[dad_id], back_populates='litters_as_dad')

    def __repr__(self):
        return f'<Puppy {self.id} ({self.name})>'