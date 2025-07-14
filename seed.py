import os
import boto3
from botocore.exceptions import NoCredentialsError
from datetime import date
from app import create_app, db
from app.models import (
    User, SiteMeta, Parent, ParentImage, Puppy, Review, HeroSection,
    AboutSection, GalleryImage, ParentRole, PuppyStatus
)
import uuid

# --- AWS S3 Configuration ---
# The script will pull these from your .env file
S3_BUCKET = os.environ.get('S3_BUCKET_NAME')
S3_REGION = os.environ.get('S3_BUCKET_REGION')

# Initialize the S3 client
s3_client = boto3.client("s3", region_name=S3_REGION)

# Local image directory
BASE_IMAGE_PATH = os.path.join(os.path.dirname(__file__), 'seed_images')


def upload_local_image_to_s3(filename, folder='general'):
    """
    Uploads a local image file from the `seed_images` directory to the S3 bucket.
    Returns the public URL of the uploaded image.
    """
    if not S3_BUCKET or not S3_REGION:
        print("Warning: S3 bucket name or region is not configured. Skipping upload.")
        return "https://via.placeholder.com/600x400.png?text=S3+Not+Configured"

    local_file_path = os.path.join(BASE_IMAGE_PATH, filename)

    if not os.path.exists(local_file_path):
        print(f"Warning: Local image file not found at {local_file_path}. Skipping.")
        return "https://via.placeholder.com/600x400.png?text=Image+Not+Found"

    # Create a unique filename for S3 to prevent overwrites
    unique_filename = f"{uuid.uuid4().hex[:8]}-{filename}"
    s3_key = f"{folder}/{unique_filename}"

    print(f"Uploading {filename} to s3://{S3_BUCKET}/{s3_key}...")
    try:
        with open(local_file_path, 'rb') as f:
            s3_client.upload_fileobj(f, S3_BUCKET, s3_key)
        
        # Construct the public URL
        url = f"https://{S3_BUCKET}.s3.{S3_REGION}.amazonaws.com/{s3_key}"
        return url
    except NoCredentialsError:
        print("Error: AWS credentials not found. Please configure your credentials.")
        return None
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

        # --- Create Site Metadata ---
        site_meta = SiteMeta(
            phone_number='520-555-1234',
            email='contact@tucsondoodles.com'
        )
        db.session.add(site_meta)

        # --- Create Homepage Content (with real image uploads) ---
        hero = HeroSection(
            title='Welcome to Tucson Golden Doodles',
            subtitle='Your new best friend is waiting for you!',
            image_url=upload_local_image_to_s3('hero-image.jpg', 'hero')
        )
        about = AboutSection(
            title='About Our Family',
            content_html='<p>We are a family-based breeder in sunny Tucson, Arizona, dedicated to raising healthy, happy, and well-socialized Golden Doodle puppies. <b>All our dogs are part of our family.</b> They live in our home, play in our yard, and are loved unconditionally.</p>',
            image_url=upload_local_image_to_s3('about-us.jpg', 'about')
        )
        db.session.add_all([hero, about])

        # --- Create Parent Dogs ---
        parent_archie = Parent(
            name='Archie', role=ParentRole.DAD, breed='F1 Mini Poodle',
            description='A gentle and intelligent sire with a beautiful apricot coat.',
            main_image_url=upload_local_image_to_s3('archie.jpg', 'parents')
        )
        parent_penelope = Parent(
            name='Penelope', role=ParentRole.MOM, breed='Cavalier King Charles Spaniel',
            description='A sweet and caring dam with a smooth and silky coat.',
            main_image_url=upload_local_image_to_s3('penelope.jpg', 'parents')
        )
        db.session.add_all([parent_archie, parent_penelope])
        db.session.commit() # Commit to get parent IDs

        # --- Create Puppies ---
        puppy_river = Puppy(
            name='River', birth_date=date(2023, 10, 1), status=PuppyStatus.AVAILABLE,
            dad_id=parent_archie.id, mom_id=parent_penelope.id,
            main_image_url=upload_local_image_to_s3('river.jpg', 'puppies')
        )
        puppy_benson = Puppy(
            name='Benson', birth_date=date(2023, 10, 1), status=PuppyStatus.RESERVED,
            dad_id=parent_archie.id, mom_id=parent_penelope.id,
            main_image_url=upload_local_image_to_s3('benson.jpg', 'puppies')
        )
        db.session.add_all([puppy_river, puppy_benson])

        # --- Create Reviews ---
        review1 = Review(
            author_name='The Smith Family',
            testimonial_text='We couldn''t be happier with our puppy!',
            is_featured=True
        )
        db.session.add(review1)

        db.session.commit()
        print("\n✅ Database seeded successfully and images uploaded to S3!")

if __name__ == '__main__':
    seed_database()