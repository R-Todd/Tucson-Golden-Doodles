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
            
            return upload_image(file_storage, folder=folder, create_responsive_versions=create_responsive)
    except Exception as e:
        print(f"Error during S3 upload for {filename}: {e}")
        return None


# Create a Flask app context to work with the database
app = create_app()

def seed_database():
    """Seeds the database with specific parents and puppies."""
    with app.app_context():
        print("Clearing existing data...")
        db.drop_all()
        db.create_all()

        print("Seeding new data and uploading images to S3...")

        # --- Basic Site and Admin Setup ---
        admin_username = os.environ.get('ADMIN_USERNAME', 'admin')
        admin_password = os.environ.get('ADMIN_PASSWORD', 'password')
        admin_user = User(username=admin_username)
        admin_user.set_password(admin_password)
        db.session.add(admin_user)
        print(f"Admin user '{admin_username}' created.")

        db.session.add(SiteMeta(phone_number='520-555-1234', email='contact@tucsondoodles.com'))

        hero_keys = upload_seed_image('hero-image.jpg', 'hero', create_responsive=True)
        db.session.add(HeroSection(
            main_title='Welcome To Tucson Golden Doodles',
            image_s3_key=hero_keys.get('original') if hero_keys else None,
            image_s3_key_large=hero_keys.get('large') if hero_keys else None
        ))

        about_keys = upload_seed_image('about-us.jpg', 'about', create_responsive=True)
        db.session.add(AboutSection(
            title='About Our Family',
            content_html='<p>Welcome to our family of doodles!</p>',
            image_s3_key=about_keys.get('original') if about_keys else None
        ))

        # --- Create Parent Dogs ---
        parent_archie = Parent(
            name='Archie', role=ParentRole.DAD, breed='F1 Mini Poodle',
            main_image_s3_key=upload_seed_image('archie.jpg', 'parents', create_responsive=True).get('original')
        )
        parent_penelope = Parent(
            name='Penelope', role=ParentRole.MOM, breed='Cavalier King Charles Spaniel',
            main_image_s3_key=upload_seed_image('penelope.jpg', 'parents', create_responsive=True).get('original')
        )
        parent_buckeye = Parent(
            name='Buckeye', role=ParentRole.DAD, breed='Merle Poodle',
            main_image_s3_key=upload_seed_image('buckeye.jpg', 'parents', create_responsive=True).get('original')
        )
        parent_minnie = Parent(
            name='Minnie', role=ParentRole.MOM, breed='Cavalier King Charles Spaniel',
            main_image_s3_key=upload_seed_image('minnie.jpg', 'parents', create_responsive=True).get('original')
        )
        db.session.add_all([parent_archie, parent_penelope, parent_buckeye, parent_minnie])
        db.session.commit()
        
        print("Parents created: Archie, Penelope, Buckeye, Minnie.")

        # --- Create Puppies and Assign to Parents ---
        
        # Litter 1: Archie & Penelope
        puppy_river = Puppy(
            name='River', birth_date=date(2024, 1, 15), status=PuppyStatus.AVAILABLE,
            dad_id=parent_archie.id, mom_id=parent_penelope.id,
            main_image_s3_key=upload_seed_image('river.jpg', 'puppies')
        )
        puppy_benson = Puppy(
            name='Benson', birth_date=date(2024, 1, 15), status=PuppyStatus.RESERVED,
            dad_id=parent_archie.id, mom_id=parent_penelope.id,
            main_image_s3_key=upload_seed_image('benson.jpg', 'puppies')
        )
        pup_ap_1 = Puppy(
            name='Coca', birth_date=date(2024, 1, 15), status=PuppyStatus.SOLD,
            dad_id=parent_archie.id, mom_id=parent_penelope.id,
            main_image_s3_key=upload_seed_image('penelope-archie-pup-1.jpg', 'puppies')
        )
        pup_ap_2 = Puppy(
            name='Spot', birth_date=date(2024, 1, 15), status=PuppyStatus.SOLD,
            dad_id=parent_archie.id, mom_id=parent_penelope.id,
            main_image_s3_key=upload_seed_image('penelope-archie-pup-2.jpg', 'puppies')
        )
        
        # Litter 2: Buckeye & Minnie
        pup_bm_1 = Puppy(
            name='Oreo', birth_date=date(2024, 2, 20), status=PuppyStatus.AVAILABLE,
            dad_id=parent_buckeye.id, mom_id=parent_minnie.id,
            main_image_s3_key=upload_seed_image('minnie-buckeye-pup-1.jpg', 'puppies')
        )
        
        # Litter 3: Buckeye & Penelope
        pup_bp_1 = Puppy(
            name='Patches', birth_date=date(2024, 3, 1), status=PuppyStatus.AVAILABLE,
            dad_id=parent_buckeye.id, mom_id=parent_penelope.id,
            main_image_s3_key=upload_seed_image('penelope-buckey-pup-1.jpg', 'puppies')
        )
        
        db.session.add_all([puppy_river, puppy_benson, pup_ap_1, pup_ap_2, pup_bm_1, pup_bp_1])
        print("Puppies created and assigned to parents.")

        # --- Final Touches: Reviews and Banners ---
        db.session.add(Review(author_name='The Todd Family', testimonial_text='We couldn''t be happier!', is_featured=True))

        announcement = AnnouncementBanner(
            is_active=True,
            main_text=" Our Newest Litter Has Arrived! ",
            sub_text="A beautiful new litter from {mom_name} & {dad_name}, born on {birth_date}.",
            button_text="Meet the Puppies",
            featured_puppy_id=puppy_river.id
        )
        db.session.add(announcement)

        db.session.commit()
        print("\n✅ Database seeded successfully and images uploaded to S3!")

if __name__ == '__main__':
    seed_database()