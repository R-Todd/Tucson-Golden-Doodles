from flask import render_template
from app.main import bp
from app.models import (
    HeroSection, AboutSection, Puppy, Review, GalleryImage, PuppyStatus
)

@bp.route('/')
def index():
    """Renders the multi-section homepage."""
    # Fetch content for each section from the database
    hero_data = HeroSection.query.first()
    about_data = AboutSection.query.first()
    available_puppies = Puppy.query.filter_by(status=PuppyStatus.AVAILABLE).order_by(Puppy.birth_date.desc()).all()
    featured_reviews = Review.query.filter_by(is_featured=True).order_by(Review.id.desc()).all()
    gallery_images = GalleryImage.query.order_by(GalleryImage.sort_order).all()

    return render_template('index.html', title='Home',
                           hero=hero_data,
                           about=about_data,
                           puppies=available_puppies,
                           reviews=featured_reviews,
                           gallery_images=gallery_images)