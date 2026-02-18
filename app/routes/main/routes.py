# app/routes/main/routes.py

from flask import render_template
from app.routes.main import bp
from app.models import (
    HeroSection,
    AboutSection,
    Puppy,
    Review,
    GalleryImage,
    PuppyStatus,
    Parent,
    AnnouncementBanner,
    Litter,
)


@bp.route('/')
def index():
    """Renders the multi-section homepage."""
    hero_data = HeroSection.query.first()
    about_data = AboutSection.query.first()
    announcement_banner = AnnouncementBanner.query.first()

    # Available puppies should be ordered by their LITTER birth date (Puppy no longer has birth_date)
    available_puppies = (
        Puppy.query
        .join(Puppy.litter)
        .filter(Puppy.status == PuppyStatus.AVAILABLE)
        .order_by(Litter.birth_date.desc(), Puppy.name.asc())
        .all()
    )

    featured_reviews = Review.query.filter_by(is_featured=True).order_by(Review.id.desc()).all()
    gallery_images = GalleryImage.query.order_by(GalleryImage.sort_order).all()
    guardian_parents = Parent.query.filter_by(is_guardian=True).all()

    # Most recent litter key should come from the Litter table directly
    most_recent_litter = Litter.query.order_by(Litter.birth_date.desc()).first()

    return render_template(
        'index.html',
        title='Home',
        hero=hero_data,
        about=about_data,
        puppies=available_puppies,
        reviews=featured_reviews,
        gallery_images=gallery_images,
        guardian_parents=guardian_parents,
        announcement_banner=announcement_banner,
        most_recent_litter=most_recent_litter,
        PuppyStatus=PuppyStatus
    )
