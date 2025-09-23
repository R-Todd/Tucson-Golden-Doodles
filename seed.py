import os
import boto3
from botocore.exceptions import NoCredentialsError
from datetime import date
from app import create_app, db
from app.models import (
    User, SiteDetails, Parent, Puppy, Review, HeroSection,
    AboutSection, GalleryImage, ParentRole, PuppyStatus, AnnouncementBanner, Breed
)
from app.utils.image_uploader import upload_image
from werkzeug.datastructures import FileStorage
import mimetypes
import re

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
    """Seeds the database with fully detailed parent and puppy data."""
    with app.app_context():
        print("Clearing existing data...")
        db.drop_all()
        db.create_all()

        print("Seeding new data and uploading all images to S3...")

        # --- Basic Site and Admin Setup ---
        db.session.add(SiteDetails(phone_number='520-555-1234', email='contact@tucsondoodles.com'))

        hero_keys = upload_seed_image('hero-image.jpg', 'hero', create_responsive=True)
        db.session.add(HeroSection(
            main_title='Tucson Golden Doodles',
            subtitle='Established 2013',
            description='Arizona Goldendoodles, Bernedoodles',
            scroll_text_main=f'Website Updated {date.today().strftime("%B %d, %Y")}',
            scroll_text_secondary='See Available Puppies Below',
            image_s3_key=hero_keys.get('original') if hero_keys else None,
            image_s3_key_large=hero_keys.get('large') if hero_keys else None
        ))

        # --- About Section Setup ---
        about_keys = upload_seed_image('about-us.jpg', 'about', create_responsive=True)
        db.session.add(AboutSection(
            title='About Our Family',
            content_html='<p>We are a family-based breeder...</p>',
            image_s3_key=about_keys.get('original') if about_keys else None
        ))

        # --- Create Breeds ---
        print("Creating breeds...")
        breeds = [
            "Golden Retriever", "Standard Poodle", "Mini Poodle",
            "Cavalier King Charles Spaniel", "Golden Doodle", "Bernese Mountain Dog",
            "Bernedoodle", "Yorkie"
        ]
        breed_objects = {}
        for breed_name in breeds:
            breed = Breed.query.filter_by(name=breed_name).first()
            if not breed:
                breed = Breed(name=breed_name)
                db.session.add(breed)
            breed_objects[breed_name] = breed
        db.session.commit()
        print("Breeds created successfully.")

        # --- Create Parents from Image Filenames ---
        print("Creating parents from seed images...")
        parent_data = {}
        for filename in os.listdir(BASE_IMAGE_PATH):
            match = re.match(r'([a-zA-Z]+)-([a-zA-Z\s]+)-(MOM|DAD)(_?[\d]*)\.jpg', filename)
            if match:
                name, breed_name, role_str, _ = match.groups()
                breed_name = breed_name.replace('_', ' ').title()
                
                if name not in parent_data:
                    parent_data[name] = {
                        'role': ParentRole[role_str],
                        'breed': breed_objects.get(breed_name),
                        'images': []
                    }
                parent_data[name]['images'].append(filename)

        parent_objects = {}
        for name, data in parent_data.items():
            main_image_file = data['images'][0]
            main_image_keys = upload_seed_image(main_image_file, 'parents', create_responsive=True)
            
            parent = Parent(
                name=name.title(),
                role=data['role'],
                breed=data['breed'],
                main_image_s3_key=main_image_keys.get('original') if main_image_keys else None,
                main_image_s3_key_large=main_image_keys.get('large') if main_image_keys else None
            )
            
            # Add alternate images
            for i, img_file in enumerate(data['images'][1:5]):
                alt_key = upload_seed_image(img_file, 'parents_alternates')
                setattr(parent, f'alternate_image_s3_key_{i+1}', alt_key)
            
            db.session.add(parent)
            parent_objects[name] = parent
        db.session.commit()
        print("Parents created successfully.")

        # --- Create Puppies and Assign to Parents ---
        print("Creating puppies...")
        archie = parent_objects.get('archie')
        penelope = parent_objects.get('penelope')
        
        if archie and penelope:
            puppy_river = Puppy(name='River', birth_date=date(2024, 1, 15), status=PuppyStatus.AVAILABLE, dad_id=archie.id, mom_id=penelope.id, main_image_s3_key=upload_seed_image('river.jpg', 'puppies'))
            db.session.add(puppy_river)
        
        db.session.commit()
        print("Puppies created.")

        # --- Final Touches: Reviews and Banners ---
        db.session.add(Review(author_name='The Smith Family', testimonial_text='We had an amazing experience...', is_featured=True))
        
        if 'puppy_river' in locals():
            announcement = AnnouncementBanner(
                is_active=True,
                main_text=" Our Newest Litter Has Arrived! ",
                sub_text="A beautiful new Cavapoo litter from {mom_name} & {dad_name}, born on {birth_date}.",
                button_text="Meet the Puppies",
                featured_puppy_id=puppy_river.id
            )
            db.session.add(announcement)
        
        db.session.commit()
        print("\n✅ Database seeded successfully with full details!")

if __name__ == '__main__':
    seed_database()