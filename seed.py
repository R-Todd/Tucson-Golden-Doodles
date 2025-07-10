from datetime import date
from app import create_app, db
from app.models import (
    SiteMeta, Parent, ParentImage, Puppy, Review, HeroSection,
    AboutSection, GalleryImage, ParentRole, PuppyStatus
)

# Create a Flask app context to work with the database
app = create_app()

def seed_database():
    """Seeds the database with sample data."""
    with app.app_context():
        print("Clearing existing data...")
        # Drop all tables and recreate them to ensure a clean slate. This is a
        # robust method for development and seeding that avoids foreign key
        # constraint issues.
        db.drop_all()
        db.create_all()

        print("Seeding new data...")

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
            image_url='img/hero_background.jpg'
        )
        about = AboutSection(
            title='About Our Family',
            content_html='<p>We are a family-based breeder in sunny Tucson, Arizona, dedicated to raising healthy, happy, and well-socialized Golden Doodle puppies. <b>All our dogs are part of our family.</b> They live in our home, play in our yard, and are loved unconditionally.</p>',
            image_url='img/about_us_family.jpg'
        )
        db.session.add_all([hero, about])

        # --- Create Parent Dogs ---
        parent_archie = Parent(
            name='Archie',
            role=ParentRole.DAD,
            breed='F1 Golden Doodle',
            description='A gentle and intelligent sire with a beautiful apricot coat. He loves playing fetch and getting belly rubs.',
            is_active=True,
            main_image_url='img/parents/archie_main.jpg'
        )
        parent_luna = Parent(
            name='Luna',
            role=ParentRole.MOM,
            breed='F1b Golden Doodle',
            description='A sweet and caring dam with a curly cream-colored coat. She is an attentive mother and loves cuddling on the couch.',
            is_active=True,
            main_image_url='img/parents/luna_main.jpg'
        )
        db.session.add_all([parent_archie, parent_luna])
        # We need to commit here to get IDs for the parents before adding images
        db.session.commit()

        # --- Create Parent Images (Gallery) ---
        archie_images = [
            ParentImage(parent_id=parent_archie.id, image_url='img/parents/archie_gallery_1.jpg', caption='Archie playing in the park'),
            ParentImage(parent_id=parent_archie.id, image_url='img/parents/archie_gallery_2.jpg', caption='Relaxing in the sun')
        ]
        luna_images = [
            ParentImage(parent_id=parent_luna.id, image_url='img/parents/luna_gallery_1.jpg', caption='Luna with her favorite toy')
        ]
        db.session.add_all(archie_images + luna_images)

        # --- Create Puppies ---
        puppy1 = Puppy(
            name='Blue Collar Male',
            birth_date=date(2023, 10, 1),
            status=PuppyStatus.AVAILABLE,
            dad_id=parent_archie.id,
            mom_id=parent_luna.id,
            main_image_url='img/puppies/puppy1.jpg'
        )
        puppy2 = Puppy(
            name='Pink Collar Female',
            birth_date=date(2023, 10, 1),
            status=PuppyStatus.RESERVED,
            dad_id=parent_archie.id,
            mom_id=parent_luna.id,
            main_image_url='img/puppies/puppy2.jpg'
        )
        db.session.add_all([puppy1, puppy2])

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

        # --- Final Commit ---
        db.session.commit()
        print("Database seeded successfully!")

if __name__ == '__main__':
    seed_database()