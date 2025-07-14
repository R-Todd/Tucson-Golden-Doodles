import os
from datetime import date
from app import create_app, db
from app.models import (
    User, SiteMeta, Parent, ParentImage, Puppy, Review, HeroSection,
    AboutSection, GalleryImage, ParentRole, PuppyStatus
)

# --- Placeholder URL for all images ---
PLACEHOLDER_URL = "https://via.placeholder.com/600x400.png?text=Tucson+Golden+Doodles"

# Create a Flask app context to work with the database
app = create_app()

def seed_database():
    """Seeds the database with sample data and an admin user."""
    with app.app_context():
        print("Clearing existing data...")
        db.drop_all()
        db.create_all()

        print("Seeding new data...")

        # --- Create Admin User ---
        admin_username = os.environ.get('ADMIN_USERNAME')
        admin_password = os.environ.get('ADMIN_PASSWORD')
        if admin_username and admin_password:
            admin_user = User(username=admin_username)
            admin_user.set_password(admin_password)
            db.session.add(admin_user)
            print(f"Admin user '{admin_username}' created.")
        else:
            print("Warning: ADMIN_USERNAME and ADMIN_PASSWORD not set in .env file. Admin user not created.")

        # --- Create Site Metadata ---
        site_meta = SiteMeta(
            phone_number='520-555-1234',
            email='contact@tucsondoodles.com',
            social_facebook_url='https://facebook.com/tucsondoodles',
            social_instagram_url='https://instagram.com/tucsondoodles'
        )
        db.session.add(site_meta)

        # --- Create Homepage Content ---
        hero = HeroSection(
            title='Welcome to Tucson Golden Doodles',
            subtitle='Your new best friend is waiting for you!',
            image_url=PLACEHOLDER_URL
        )
        about = AboutSection(
            title='About Our Family',
            content_html='<p>We are a family-based breeder in sunny Tucson, Arizona, dedicated to raising healthy, happy, and well-socialized Golden Doodle puppies. <b>All our dogs are part of our family.</b> They live in our home, play in our yard, and are loved unconditionally.</p>',
            image_url=PLACEHOLDER_URL
        )
        db.session.add_all([hero, about])

        # --- Create Parent Dogs ---
        parent_archie = Parent(
            name='Archie',
            role=ParentRole.DAD,
            breed='F1 Golden Doodle',
            description='A gentle and intelligent sire with a beautiful apricot coat. He loves playing fetch and getting belly rubs.',
            is_active=True,
            main_image_url=PLACEHOLDER_URL
        )
        parent_penelope = Parent(
            name='Penelope',
            role=ParentRole.MOM,
            breed='F1b Golden Doodle',
            description='A sweet and caring dam with a curly cream-colored coat. She is an attentive mother and loves cuddling on the couch.',
            is_active=True,
            main_image_url=PLACEHOLDER_URL
        )
        db.session.add_all([parent_archie, parent_penelope])
        db.session.commit()

        # --- Create Parent Images (Gallery) ---
        archie_images = [
            ParentImage(parent_id=parent_archie.id, image_url=PLACEHOLDER_URL, caption='Archie playing in the park'),
            ParentImage(parent_id=parent_archie.id, image_url=PLACEHOLDER_URL, caption='Relaxing in the sun')
        ]
        penelope_images = [
            ParentImage(parent_id=parent_penelope.id, image_url=PLACEHOLDER_URL, caption='Penelope with her favorite toy')
        ]
        db.session.add_all(archie_images + penelope_images)

        # --- Create Puppies ---
        puppy_river = Puppy(
            name='River',
            birth_date=date(2023, 10, 1),
            status=PuppyStatus.AVAILABLE,
            dad_id=parent_archie.id,
            mom_id=parent_penelope.id,
            main_image_url=PLACEHOLDER_URL
        )
        puppy_benson = Puppy(
            name='Benson',
            birth_date=date(2023, 10, 1),
            status=PuppyStatus.RESERVED,
            dad_id=parent_archie.id,
            mom_id=parent_penelope.id,
            main_image_url=PLACEHOLDER_URL
        )
        db.session.add_all([puppy_river, puppy_benson])

        # --- Create Reviews ---
        review1 = Review(
            author_name='The Smith Family',
            testimonial_text='We couldn''t be happier with our puppy! The entire process was wonderful and we have the sweetest new family member.',
            is_featured=True
        )
        review2 = Review(
            author_name='Jane D.',
            testimonial_text='Our vet was so impressed with how healthy and well-socialized our new puppy was. Thank you!',
            is_featured=False
        )
        db.session.add_all([review1, review2])

        db.session.commit()
        print("Database seeded successfully with placeholder images and updated names!")

if __name__ == '__main__':
    seed_database()