import os
from datetime import date
from werkzeug.datastructures import FileStorage

from app import create_app
from app.models import (
    db,
    User,
    SiteDetails,
    Parent,
    ParentImage,
    Puppy,
    Review,
    HeroSection,
    AboutSection,
    GalleryImage,
    AnnouncementBanner,
    ParentRole,
    PuppyStatus,
    Litter,
)

from app.utils.image_uploader import upload_image


# ======================================================
# VALIDATION HELPERS
# ======================================================

def require_env(var_name: str) -> str:
    """Return required env var value or raise a clear error."""
    value = os.environ.get(var_name)
    if value is None or str(value).strip() == "":
        raise RuntimeError(f"{var_name} is required to run seed.py.")
    return value


def validate_seed_requirements() -> None:
    """Fail fast if required env vars for seeding are missing."""
    # Admin credentials (single-admin model)
    require_env("ADMIN_USERNAME")
    require_env("ADMIN_PASSWORD")

    # App secrets / DB
    require_env("SECRET_KEY")
    require_env("DATABASE_URL")

    # S3 requirements (you requested: fail if missing)
    require_env("S3_BUCKET_NAME")
    require_env("S3_BUCKET_REGION")
    require_env("AWS_ACCESS_KEY_ID")
    require_env("AWS_SECRET_ACCESS_KEY")


# ======================================================
# REAL S3 SEED IMAGE HELPER
# ======================================================

def upload_seed_image(filename, folder, responsive=False):
    image_path = os.path.join("seed_images", filename)

    if not os.path.exists(image_path):
        print(f"Seed image not found: {image_path}")
        return None

    with open(image_path, "rb") as f:
        file_storage = FileStorage(
            stream=f,
            filename=filename,
            content_type="image/jpeg"
        )

        result, err = upload_image(
            file_storage,
            folder=folder,
            create_responsive_versions=responsive
        )

        if err:
            print(f"Warning: Upload rejected (skipping): {filename} — {err}")
            return None

        return result

# ======================================================
# SEED SCRIPT
# ======================================================

app = create_app()

with app.app_context():
    # Fail fast on missing config (you requested strict S3 requirements)
    validate_seed_requirements()

    print("Clearing existing data...")

    # IMPORTANT:
    # We rely on Alembic migrations to create/alter tables.
    # Run `flask db upgrade` before `python seed.py`.
    #
    # Here we only clear rows to reseed deterministically.
    #
    # Delete order matters due to foreign keys.
    # Delete order matters due to foreign keys.
    db.session.query(AnnouncementBanner).delete()
    db.session.query(ParentImage).delete()
    db.session.query(Puppy).delete()
    db.session.query(Litter).delete()
    db.session.query(Parent).delete()
    db.session.query(Review).delete()
    db.session.query(GalleryImage).delete()
    db.session.query(HeroSection).delete()
    db.session.query(AboutSection).delete()
    db.session.query(SiteDetails).delete()
    db.session.query(User).delete()
    db.session.commit()

    # ======================================================
    # ADMIN (FROM .env) — REQUIRED
    # ======================================================

    admin_username = require_env("ADMIN_USERNAME")
    admin_password = require_env("ADMIN_PASSWORD")

    admin = User(username=admin_username)
    admin.set_password(admin_password)
    db.session.add(admin)

    # ======================================================
    # SITE DETAILS
    # ======================================================

    site_details = SiteDetails(
        phone_number="520-123-4567",
        email="info@tucsongoldendoodles.com"
    )
    db.session.add(site_details)

    db.session.commit()
    print("Created admin + site details")

    # ======================================================
    # PARENTS
    # ======================================================

    parent_archie = Parent(
        name="Archie",
        role=ParentRole.DAD,
        breed="Cavapoo",
        birth_date=date(2021, 5, 1),
        weight_kg=8,
        height_cm=35,
        description="Friendly and intelligent sire."
    )

    parent_penelope = Parent(
        name="Penelope",
        role=ParentRole.MOM,
        breed="Cavapoo",
        birth_date=date(2020, 3, 10),
        weight_kg=7,
        height_cm=32,
        description="Gentle and affectionate dam."
    )

    parent_buckeye = Parent(
        name="Buckeye",
        role=ParentRole.DAD,
        breed="Mini Goldendoodle",
        birth_date=date(2021, 8, 15),
        weight_kg=12,
        height_cm=40,
        description="Energetic and playful sire."
    )

    parent_minnie = Parent(
        name="Minnie",
        role=ParentRole.MOM,
        breed="Mini Goldendoodle",
        birth_date=date(2020, 6, 5),
        weight_kg=10,
        height_cm=38,
        description="Sweet and nurturing dam."
    )

    db.session.add_all([
        parent_archie,
        parent_penelope,
        parent_buckeye,
        parent_minnie
    ])
    db.session.commit()

    # Upload responsive parent main images
    for parent, filename in [
        (parent_archie, "archie.jpg"),
        (parent_penelope, "penelope.jpg"),
        (parent_buckeye, "buckeye.jpg"),
        (parent_minnie, "minnie.jpg"),
    ]:
        keys = upload_seed_image(filename, "parents", responsive=True)
        if keys:
            parent.main_image_s3_key_small = keys.get("small")
            parent.main_image_s3_key_medium = keys.get("medium")
            parent.main_image_s3_key_large = keys.get("large")
            parent.main_image_s3_key = keys.get("original")

    db.session.commit()

    # Alternate parent images
    alternate_images = [
        ("archie-2.jpg", parent_archie.id),
        ("archie-3.jpg", parent_archie.id),
        ("penelope-2.jpg", parent_penelope.id),
        ("penelope-3.jpg", parent_penelope.id),
        ("buckeye-2.jpg", parent_buckeye.id),
        ("minnie-2.jpg", parent_minnie.id),
        ("minnie-3.jpg", parent_minnie.id),
    ]

    for filename, parent_id in alternate_images:
        key = upload_seed_image(filename, "parents")
        if key:
            db.session.add(
                ParentImage(parent_id=parent_id, image_s3_key=key)
            )

    db.session.commit()
    print("Uploaded parent images")

    # ======================================================
    # LITTERS
    # ======================================================

    litter_ap = Litter(
        mom_id=parent_penelope.id,
        dad_id=parent_archie.id,
        birth_date=date(2024, 1, 15),
        breed_name="Cavapoo",
        description="Affectionate and calm Cavapoo litter.",
        expected_weight="15–25 lbs"
    )

    litter_bm = Litter(
        mom_id=parent_minnie.id,
        dad_id=parent_buckeye.id,
        birth_date=date(2024, 2, 20),
        breed_name="Mini Goldendoodle",
        description="Playful and intelligent Mini Goldendoodles.",
        expected_weight="20–30 lbs"
    )

    db.session.add_all([litter_ap, litter_bm])
    db.session.commit()

    print("Created litters")

    # ======================================================
    # PUPPIES
    # ======================================================

    puppies = [
        ("River", "Apricot", PuppyStatus.AVAILABLE, litter_ap.id, "river.jpg"),
        ("Benson", "Cream", PuppyStatus.RESERVED, litter_ap.id, "benson.jpg"),
        ("Oreo", "Merle", PuppyStatus.AVAILABLE, litter_bm.id, "minnie-buckeye-pup-1.jpg"),
    ]

    for name, coat, status, litter_id, image_file in puppies:
        key = upload_seed_image(image_file, "puppies")
        db.session.add(
            Puppy(
                name=name,
                coat=coat,
                status=status,
                litter_id=litter_id,
                main_image_s3_key=key
            )
        )

    db.session.commit()
    print("Created puppies")

    # ======================================================
    # GALLERY
    # ======================================================

    gallery_files = ["hero-image.jpg", "about-us.jpg"]

    for filename in gallery_files:
        key = upload_seed_image(filename, "gallery")
        if key:
            db.session.add(GalleryImage(image_s3_key=key))

    # ======================================================
    # REVIEWS
    # ======================================================

    db.session.add_all([
        Review(
            author_name="Sarah T.",
            testimonial_text="Wonderful experience from start to finish.",
            is_featured=True
        ),
        Review(
            author_name="Michael R.",
            testimonial_text="Healthy, happy puppies raised with love.",
            is_featured=False
        )
    ])

    # ======================================================
    # HERO / ABOUT / BANNER
    # ======================================================

    hero_keys = upload_seed_image("hero-image.jpg", "hero", responsive=True)

    hero = HeroSection(
        main_title="Premium Goldendoodles in Tucson",
        subtitle="Healthy, happy, home-raised puppies.",
        description="Ethically bred, family-raised companions in Arizona.",
        scroll_text_main="Now Accepting Deposits",
        scroll_text_secondary="See Available Puppies Below",
        image_s3_key=hero_keys.get("original") if hero_keys else None,
        image_s3_key_small=hero_keys.get("small") if hero_keys else None,
        image_s3_key_medium=hero_keys.get("medium") if hero_keys else None,
        image_s3_key_large=hero_keys.get("large") if hero_keys else None,
    )

    about_keys = upload_seed_image("about-us.jpg", "about", responsive=True)

    about = AboutSection(
        title="About Tucson Golden Doodles",
        content_html="<p>We raise well-socialized, healthy puppies in a loving environment.</p>",
        image_s3_key=about_keys.get("original") if about_keys else None,
        image_s3_key_small=about_keys.get("small") if about_keys else None,
        image_s3_key_medium=about_keys.get("medium") if about_keys else None,
        image_s3_key_large=about_keys.get("large") if about_keys else None,
    )

    banner = AnnouncementBanner(
        is_active=True,
        main_text="Now accepting deposits for upcoming litters!",
        sub_text="A beautiful new litter is now available.",
        button_text="Meet the Puppies"
    )

    db.session.add_all([hero, about, banner])
    db.session.commit()

    print("Created hero/about/banner")
    print(" Database seeded successfully.")