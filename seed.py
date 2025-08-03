import os
import boto3
from botocore.exceptions import NoCredentialsError
from datetime import date
from app import create_app, db
from app.models import (
    User, SiteMeta, Parent, Puppy, Review, HeroSection,
    AboutSection, GalleryImage, ParentRole, PuppyStatus, AnnouncementBanner
)
from app.utils.image_uploader import upload_image
from werkzeug.datastructures import FileStorage
import mimetypes

# --- AWS S3 Configuration ---
S3_BUCKET = os.environ.get('S3_BUCKET_NAME')
S3_REGION = os.environ.get('S3_BUCKET_REGION')

# Local image directory
BASE_IMAGE_PATH = os.path.join(os.path.dirname(__file__), 'seed_images')

def upload_seed_image(filename, folder='general', create_responsive=False):
    """
    Uploads a local image file from the seed_images directory to S3
    and returns the S3 key or a dictionary of keys.
    """
    if not S3_BUCKET or not S3_REGION:
        print(f"Warning: S3 not configured. Cannot upload {filename}.")
        return None

    local_file_path = os.path.join(BASE_IMAGE_PATH, filename)
    if not os.path.exists(local_file_path):
        print(f"Warning: Local image file not found: {local_file_path}.")
        return None

    print(f"Uploading {filename} to S3 in folder '{folder}'...")
    try:
        with open(local_file_path, 'rb') as f:
            mime_type, _ = mimetypes.guess_type(local_file_path)
            mime_type = mime_type or "application/octet-stream"
            
            file_storage = FileStorage(f, filename=filename, content_type=mime_type)
            
            # The upload_image utility now returns S3 keys
            return upload_image(file_storage, folder=folder, create_responsive_versions=create_responsive)
    except Exception as e:
        print(f"Error during S3 upload for {filename}: {e}")
        return None


# Create a Flask app context to work with the database
app = create_app()

def seed_database():
    """Seeds the database with sample data, saving S3 keys for images."""
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
            print("Warning: ADMIN_USERNAME and ADMIN_PASSWORD not set. Admin user not created.")

        site_meta = SiteMeta(phone_number='520-555-1234', email='contact@tucsondoodles.com')
        db.session.add(site_meta)

        # --- Homepage Content (with S3 keys) ---
        hero_keys = upload_seed_image('hero-image.jpg', 'hero', create_responsive=True)
        about_keys = upload_seed_image('about-us.jpg', 'about', create_responsive=True)

        if hero_keys:
            hero = HeroSection(
                main_title='Copper Skye Doodles',
                subtitle='Established 2001',
                description='Arizona Goldendoodles, Bernedoodles & Golden Mountain Doodles',
                scroll_text_main=f'Website Updated {date.today().strftime("%B %d, %Y")}',
                scroll_text_secondary='See Available Puppies Below',
                image_s3_key=hero_keys.get('original'),
                image_s3_key_small=hero_keys.get('small'),
                image_s3_key_medium=hero_keys.get('medium'),
                image_s3_key_large=hero_keys.get('large')
            )
            db.session.add(hero)

        if about_keys:
            about = AboutSection(
                title='About Our Family',
                content_html='<p>We are a family-based breeder...<b>All our dogs are part of our family.</b></p>',
                image_s3_key=about_keys.get('original'),
                image_s3_key_small=about_keys.get('small'),
                image_s3_key_medium=about_keys.get('medium'),
                image_s3_key_large=about_keys.get('large')
            )
            db.session.add(about)

        # --- Parent Dogs (with S3 keys) ---
        archie_keys = upload_seed_image('archie.jpg', 'parents', create_responsive=True)
        parent_archie = Parent(
            name='Archie', role=ParentRole.DAD, breed='F1 Mini Poodle',
            description='A gentle and intelligent sire with a beautiful apricot coat.',
            main_image_s3_key=archie_keys.get('original') if archie_keys else None,
            main_image_s3_key_small=archie_keys.get('small') if archie_keys else None,
            main_image_s3_key_medium=archie_keys.get('medium') if archie_keys else None,
            main_image_s3_key_large=archie_keys.get('large') if archie_keys else None,
            alternate_image_s3_key_1=upload_seed_image('archie_gallery_1.jpg', 'parents_alternates'),
            alternate_image_s3_key_2=upload_seed_image('archie_gallery_2.jpg', 'parents_alternates')
        )
        
        penelope_keys = upload_seed_image('penelope.jpg', 'parents', create_responsive=True)
        parent_penelope = Parent(
            name='Penelope', role=ParentRole.MOM, breed='Cavalier King Charles Spaniel',
            description='A sweet and caring dam with a smooth and silky coat.',
            main_image_s3_key=penelope_keys.get('original') if penelope_keys else None,
            main_image_s3_key_small=penelope_keys.get('small') if penelope_keys else None,
            main_image_s3_key_medium=penelope_keys.get('medium') if penelope_keys else None,
            main_image_s3_key_large=penelope_keys.get('large') if penelope_keys else None,
            alternate_image_s3_key_1=upload_seed_image('penny_main.jpg', 'parents_alternates'),
            alternate_image_s3_key_2=upload_seed_image('luna_gallery_1.jpg', 'parents_alternates')
        )
        db.session.add_all([parent_archie, parent_penelope])
        db.session.commit()

        # --- Puppies (with S3 keys) ---
        puppy_river = Puppy(
            name='River', birth_date=date(2023, 10, 1), status=PuppyStatus.AVAILABLE,
            dad_id=parent_archie.id, mom_id=parent_penelope.id,
            main_image_s3_key=upload_seed_image('river.jpg', 'puppies')
        )
        
        puppy_benson = Puppy(
            name='Benson', birth_date=date(2023, 10, 1), status=PuppyStatus.RESERVED,
            dad_id=parent_archie.id, mom_id=parent_penelope.id,
            main_image_s3_key=upload_seed_image('benson.jpg', 'puppies')
        )
        db.session.add_all([puppy_river, puppy_benson])

        review1 = Review(author_name='The Smith Family', testimonial_text='We couldn''t be happier!', is_featured=True)
        db.session.add(review1)

        # --- Announcement Banner ---
        announcement = AnnouncementBanner(
            is_active=True,
            main_text="✨ Our Newest Litter Has Arrived! ✨",
            sub_text="A beautiful new litter from {mom_name} & {dad_name}, born on {birth_date}.",
            button_text="Meet the Puppies",
            featured_puppy_id=puppy_river.id
        )
        db.session.add(announcement)

        db.session.commit()
        print("\n✅ Database seeded successfully and images uploaded to S3!")

if __name__ == '__main__':
    seed_database()