# app/models/review_models.py
"""
Defines the Review model for storing customer testimonials.

Also defines ReviewImage to support multiple images per review.
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
    # Controls ordering of reviews (lower appears first).
    sort_order = db.Column(db.Integer, default=0, nullable=False, index=True)

    # Ordered images associated with this review (0..N).
    images = db.relationship(
        'ReviewImage',
        backref='review',
        lazy='select',
        cascade='all, delete-orphan',
        order_by='ReviewImage.sort_order',
    )

    def __repr__(self):
        """Provides a developer-friendly representation of the Review object."""
        return f'<Review by {self.author_name}>'


class ReviewImage(db.Model):
    """
    Represents a single image attached to a Review.

    Images are stored as S3 keys; sort_order controls display order.
    """

    __tablename__ = 'review_images'

    id = db.Column(db.Integer, primary_key=True)
    review_id = db.Column(db.Integer, db.ForeignKey('review.id'), nullable=False, index=True)

    # S3 key/path for the image (e.g., "reviews/abc123.jpg")
    s3_key = db.Column(db.String(512), nullable=False)

    # Optional caption (admin/future UI)
    caption = db.Column(db.String(200), nullable=True)

    # Controls thumbnail/display ordering (lower first)
    sort_order = db.Column(db.Integer, default=0, nullable=False, index=True)

    def __repr__(self):
        return f'<ReviewImage review_id={self.review_id} sort_order={self.sort_order}>'