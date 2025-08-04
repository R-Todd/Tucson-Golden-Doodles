# app/models/review_models.py
"""
Defines the Review model for storing customer testimonials.
"""

from . import db

class Review(db.Model):
    """
    Represents a customer review or testimonial.

    This model is used to display feedback from past customers on the website.
    """
    id = db.Column(db.Integer, primary_key=True)
    author_name = db.Column(db.String(100), nullable=False)
    testimonial_text = db.Column(db.Text, nullable=False)
    # A flag to highlight specific reviews on the homepage or other prominent areas.
    is_featured = db.Column(db.Boolean, default=False, nullable=False)

    def __repr__(self):
        """Provides a developer-friendly representation of the Review object."""
        return f'<Review by {self.author_name}>'