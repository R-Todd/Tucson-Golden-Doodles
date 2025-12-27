# app/routes/main/routes.py

from flask import render_template
from app.routes.main import bp
from app.models import (
    HeroSection, AboutSection, Puppy, Review, GalleryImage, PuppyStatus, Parent,
    AnnouncementBanner, Litter  # Added Litter to imports
)
from itertools import groupby
from collections import OrderedDict

@bp.route('/')
def index():
    """Renders the multi-section homepage."""
    hero_data = HeroSection.query.first()
    about_data = AboutSection.query.first()
    announcement_banner = AnnouncementBanner.query.first()
    
    # Updated: Join with Litter to filter available puppies by the Litter's birth_date
    available_puppies = Puppy.query.join(Litter).filter(
        Puppy.status == PuppyStatus.AVAILABLE
    ).order_by(Litter.birth_date.desc()).all()
    
    featured_reviews = Review.query.filter_by(is_featured=True).order_by(Review.id.desc()).all()
    gallery_images = GalleryImage.query.order_by(GalleryImage.sort_order).all()
    guardian_parents = Parent.query.filter_by(is_guardian=True).all()

    # Updated logic for identifying the most recent litter
    most_recent_litter_key = None
    all_puppies = Puppy.query.join(Litter).order_by(Litter.birth_date.desc()).all()
    
    if all_puppies:
        # Group by the Litter object itself rather than a tuple of attributes
        # This keeps the logic consistent with the new model structure
        keyfunc = lambda p: p.litter
        first_group = next(groupby(all_puppies, key=keyfunc), None)
        if first_group:
            # most_recent_litter_key will now be a Litter object
            most_recent_litter_key, _ = first_group

    return render_template('index.html', title='Home',
                           hero=hero_data,
                           about=about_data,
                           puppies=available_puppies,
                           reviews=featured_reviews, 
                           gallery_images=gallery_images,
                           guardian_parents=guardian_parents,
                           announcement_banner=announcement_banner,
                           most_recent_litter_key=most_recent_litter_key,
                           PuppyStatus=PuppyStatus)