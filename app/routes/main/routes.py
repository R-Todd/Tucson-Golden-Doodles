# app/routes/main/routes.py
from flask import render_template
from app.routes.main import bp
from app.models import (
    HeroSection, AboutSection, Puppy, Review, GalleryImage, PuppyStatus, Parent,
    AnnouncementBanner
)
from itertools import groupby
from collections import OrderedDict

@bp.route('/')
def index():
    """Renders the multi-section homepage."""
    hero_data = HeroSection.query.first()
    about_data = AboutSection.query.first()
    announcement_banner = AnnouncementBanner.query.first()
    available_puppies = Puppy.query.filter_by(status=PuppyStatus.AVAILABLE).order_by(Puppy.birth_date.desc()).all()
    featured_reviews = Review.query.filter_by(is_featured=True).order_by(Review.id.desc()).all()
    gallery_images = GalleryImage.query.order_by(GalleryImage.sort_order).all()
    guardian_parents = Parent.query.filter_by(is_guardian=True).all()

    most_recent_litter_key = None
    all_puppies = Puppy.query.order_by(Puppy.birth_date.desc()).all()
    if all_puppies:
        keyfunc = lambda p: (p.birth_date, p.mom, p.dad)
        first_group = next(groupby(all_puppies, key=keyfunc), None)
        if first_group:
            most_recent_litter_key, _ = first_group

    return render_template('index.html', title='Home',
                           hero=hero_data,
                           about=about_data,
                           puppies=available_puppies,
                           reviews=featured_reviews,
                           gallery_images=gallery_images,
                           guardian_parents=guardian_parents,
                           announcement_banner=announcement_banner,
                           most_recent_litter_key=most_recent_litter_key)