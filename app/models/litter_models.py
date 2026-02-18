from . import db
from datetime import date


class Litter(db.Model):
    """
    Represents a breeding pairing (Mom + Dad) and shared litter metadata.
    Each puppy belongs to exactly one litter.
    """

    __tablename__ = "litter"

    id = db.Column(db.Integer, primary_key=True)

    # Parent relationships
    mom_id = db.Column(db.Integer, db.ForeignKey("parent.id"), nullable=False)
    dad_id = db.Column(db.Integer, db.ForeignKey("parent.id"), nullable=False)

    # Shared litter information
    birth_date = db.Column(db.Date, nullable=False)
    breed_name = db.Column(db.String(120), nullable=True)
    description = db.Column(db.Text, nullable=True)
    expected_weight = db.Column(db.String(120), nullable=True)

    # Relationship to puppies
    puppies = db.relationship(
        "Puppy",
        backref="litter",
        lazy=True,
        cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Litter {self.id} - {self.breed_name or 'Unnamed'}>"
