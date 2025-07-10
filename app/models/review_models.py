from . import db

# Customer reviews
class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    author_name = db.Column(db.String(100), nullable=False)
    testimonial_text = db.Column(db.Text, nullable=False)
    is_featured = db.Column(db.Boolean, default=False, nullable=False)

    def __repr__(self):
        return f'<Review by {self.author_name}>'