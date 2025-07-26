import os
import boto3
from botocore.exceptions import NoCredentialsError
from datetime import date
from app import create_app, db
from app.models import (
    User, SiteMeta, Parent, Puppy, Review, HeroSection,
    AboutSection, GalleryImage, ParentRole, PuppyStatus
)
from app.utils.image_uploader import upload_image, RESPONSIVE_SIZES # Import the uploader
from werkzeug.datastructures import FileStorage
import mimetypes

# --- AWS S3 Configuration ---
S3_BUCKET = os.environ.get('S3_BUCKET_NAME')
S3_REGION = os.environ.get('S3_BUCKET_REGION')

# Local image directory
BASE_IMAGE_PATH = os.path.join(os.path.dirname(__file__), 'seed_images')

def upload_seed_image(filename, folder='general', create_responsive=False):
    """
    Uploads a local image file and returns either a single URL or a dictionary of URLs.
    """
    if not S3_BUCKET or not S3_REGION:
        print(f"Warning: S3 not configured. Using placeholder for {filename}.")
        return "https://via.placeholder.com/800x600.png?text=S3+Not+Configured"

    local_file_path = os.path.join(BASE_IMAGE_PATH, filename)
    if not os.path.exists(local_file_path):
        print(f"Warning: Local image file not found: {local_file_path}. Using placeholder.")
        return "https://via.placeholder.com/800x600.png?text=Image+Not+Found"

    print(f"Uploading {filename} to S3 in folder '{folder}'...")
    try:
        with open(local_file_path, 'rb') as f:
            # Manually determine the content type
            content_type, _ = mimetypes.guess_type(local_file_path)
            if content_type is None:
                content_type = 'application/octet-stream' # A generic fallback

            # Wrap the file in FileStorage, now with the correct content_type
            file_storage = FileStorage(f, filename=filename, content_type=content_type)
            
            # Use the main application's uploader
            return upload_image(file_storage, folder=folder, create_responsive_versions=create_responsive)
    except Exception as e:
        print(f"Error during S3 upload for {filename}: {e}")
        return None


# Create a Flask app context to work with the database
app = create_app()

def seed_database():
    """Seeds the database with sample data, uploading images to S3."""
    with app.app_context():
        print("Clearing existing data...")
        db.drop_all()
        db.create_all()

        print("Seeding new data and uploading images to S3...")

        # --- Create Admin User ---
        admin_username = os.environ.get('ADMIN_USERNAME')
        admin_password = os.environ.get('ADMIN_PASSWORD')
        if admin_username and admin_password:
            admin_user = User(username=admin_username)
            admin_user.set_password(admin_password)
            db.session.add(admin_user)
            print(f"Admin user '{admin_username}' created.")
        else:
            print("Warning: ADMIN_USERNAME and ADMIN_PASSWORD not set in .env. Admin user not created.")

        site_meta = SiteMeta(phone_number='520-555-1234', email='contact@tucsondoodles.com')
        db.session.add(site_meta)

        # --- Homepage Content (with responsive images) ---
        hero_urls = upload_seed_image('hero-image.jpg', 'hero', create_responsive=True)
        about_urls = upload_seed_image('about-us.jpg', 'about', create_responsive=True)

        hero = HeroSection(
            title='Welcome to Tucson Golden Doodles',
            subtitle='Your new best friend is waiting for you!',
            image_url=hero_urls.get('original'),
            image_url_small=hero_urls.get('small'),
            image_url_medium=hero_urls.get('medium'),
            image_url_large=hero_urls.get('large')
        )
        about = AboutSection(
            title='About Our Family',
            content_html='<p>We are a family-based breeder in sunny Tucson, Arizona, dedicated to raising healthy, happy, and well-socialized Golden Doodle puppies. <b>All our dogs are part of our family.</b> They live in our home, play in our yard, and are loved unconditionally.</p>',
            image_url=about_urls.get('original'),
            image_url_small=about_urls.get('small'),
            image_url_medium=about_urls.get('medium'),
            image_url_large=about_urls.get('large')
        )
        db.session.add_all([hero, about])

        # --- Parent Dogs (with responsive images) ---
        archie_urls = upload_seed_image('archie.jpg', 'parents', create_responsive=True)
        parent_archie = Parent(
            name='Archie', role=ParentRole.DAD, breed='F1 Mini Poodle',
            description='A gentle and intelligent sire with a beautiful apricot coat.',
            main_image_url=archie_urls.get('original'),
            main_image_url_small=archie_urls.get('small'),
            main_image_url_medium=archie_urls.get('medium'),
            main_image_url_large=archie_urls.get('large'),
            alternate_image_url_1=upload_seed_image('archie_gallery_1.jpg', 'parents_alternates'),
            alternate_image_url_2=upload_seed_image('archie_gallery_2.jpg', 'parents_alternates')
        )
        
        penelope_urls = upload_seed_image('penelope.jpg', 'parents', create_responsive=True)
        parent_penelope = Parent(
            name='Penelope', role=ParentRole.MOM, breed='Cavalier King Charles Spaniel',
            description='A sweet and caring dam with a smooth and silky coat.',
            main_image_url=penelope_urls.get('original'),
            main_image_url_small=penelope_urls.get('small'),
            main_image_url_medium=penelope_urls.get('medium'),
            main_image_url_large=penelope_urls.get('large'),
            alternate_image_url_1=upload_seed_image('penny_main.jpg', 'parents_alternates'),
            alternate_image_url_2=upload_seed_image('luna_gallery_1.jpg', 'parents_alternates')
        )
        db.session.add_all([parent_archie, parent_penelope])
        db.session.commit()

        # --- Puppies (single image upload) ---
        puppy_river = Puppy(
            name='River', birth_date=date(2023, 10, 1), status=PuppyStatus.AVAILABLE,
            dad_id=parent_archie.id, mom_id=parent_penelope.id,
            main_image_url=upload_seed_image('river.jpg', 'puppies')
        )
        puppy_benson = Puppy(
            name='Benson', birth_date=date(2023, 10, 1), status=PuppyStatus.RESERVED,
            dad_id=parent_archie.id, mom_id=parent_penelope.id,
            main_image_url=upload_seed_image('benson.jpg', 'puppies')
        )
        db.session.add_all([puppy_river, puppy_benson])

        review1 = Review(author_name='The Smith Family', testimonial_text='We couldn''t be happier with our puppy!', is_featured=True)
        db.session.add(review1)

        db.session.commit()
        print("\n✅ Database seeded successfully and images uploaded to S3!")

if __name__ == '__main__':
    seed_database()