# app/routes/main/routes.py

from flask import render_template
from sqlalchemy import func

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


@bp.route("/")
def index():
    """Renders the multi-section homepage."""
    hero_data = HeroSection.query.first()
    about_data = AboutSection.query.first()
    announcement_banner = AnnouncementBanner.query.first()

    # --- Homepage: show ONLY 3 most recent AVAILABLE puppies ---
    available_puppies = (
        Puppy.query
        .join(Puppy.litter)
        .filter(Puppy.status == PuppyStatus.AVAILABLE)
        .order_by(Litter.birth_date.desc(), Puppy.name.asc())
        .limit(3)
        .all()
    )

    # --- Homepage: Reviews should never render blank cards ---
    # Prefer featured reviews, but require non-empty author + text.
    non_empty_review_filter = (
        func.length(func.trim(Review.author_name)) > 0,
        func.length(func.trim(Review.testimonial_text)) > 0,
    )

    featured_reviews = (
        Review.query
        .filter(Review.is_featured.is_(True), *non_empty_review_filter)
        .order_by(Review.id.desc())
        .all()
    )

    # Fallback: if featured reviews are empty/placeholder, show recent valid reviews instead
    if not featured_reviews:
        featured_reviews = (
            Review.query
            .filter(*non_empty_review_filter)
            .order_by(Review.id.desc())
            .limit(6)
            .all()
        )

    gallery_images = GalleryImage.query.order_by(GalleryImage.sort_order).all()
    guardian_parents = Parent.query.filter_by(is_guardian=True).all()

    most_recent_litter = Litter.query.order_by(Litter.birth_date.desc()).first()

    return render_template(
        "index.html",
        title="Home",
        hero=hero_data,
        about=about_data,
        puppies=available_puppies,
        reviews=featured_reviews,
        gallery_images=gallery_images,
        guardian_parents=guardian_parents,
        announcement_banner=announcement_banner,
        most_recent_litter=most_recent_litter,
        PuppyStatus=PuppyStatus,
    )