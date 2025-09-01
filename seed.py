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
    """Seeds the database with fully detailed parent and puppy data."""
    with app.app_context():
        print("Clearing existing data...")
        db.drop_all()
        db.create_all()

        print("Seeding new data and uploading all images to S3...")

        # --- Basic Site and Admin Setup ---
        # admin_username = os.environ.get('ADMIN_USERNAME', 'admin')
        # admin_password = os.environ.get('ADMIN_PASSWORD', 'password')
        # admin_user = User(username=admin_username)
        # admin_user.set_password(admin_password)
        # db.session.add(admin_user)
        # print(f"Admin user '{admin_username}' created.")
        # - Admin creation logic is now removed.


        db.session.add(SiteMeta(phone_number='520-555-1234', email='contact@tucsondoodles.com'))

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

        about_keys = upload_seed_image('about-us.jpg', 'about', create_responsive=True)
        db.session.add(AboutSection(
            title='About Our Family',
            content_html='<p>We are a family-based breeder located in the heart of Tucson, Arizona. Our passion for doodles started over a decade ago, and since then, we have been dedicated to raising healthy, happy, and well-socialized puppies. <b>All our dogs are part of our family</b>, living in our home and receiving constant love and attention. We believe this makes all the difference in their temperament and development.</p>',
            image_s3_key=about_keys.get('original') if about_keys else None
        ))

        # --- Create Fully Detailed Parent Dogs ---
        
        # Archie
        archie_main_keys = upload_seed_image('archie.jpg', 'parents', create_responsive=True)
        parent_archie = Parent(
            name='Archie',
            role=ParentRole.DAD,
            breed='F1 Mini Poodle',
            birth_date=date(2021, 5, 12),
            weight_kg=8.5,
            height_cm=38,
            description="Archie is the heart of our program. He is a gentle and intelligent sire with a stunning apricot coat and a calm, loving demeanor. He passes on his wonderful temperament and sharp intellect to his puppies, making them perfect family companions. He loves playing fetch and getting belly rubs.",
            main_image_s3_key=archie_main_keys.get('original') if archie_main_keys else None,
            main_image_s3_key_large=archie_main_keys.get('large') if archie_main_keys else None,
            alternate_image_s3_key_1=upload_seed_image('archie-2.jpg', 'parents_alternates'),
            alternate_image_s3_key_2=upload_seed_image('archie-3.jpg', 'parents_alternates')
        )

        # Penelope
        penelope_main_keys = upload_seed_image('penelope.jpg', 'parents', create_responsive=True)
        parent_penelope = Parent(
            name='Penelope',
            role=ParentRole.MOM,
            breed='Cavalier King Charles Spaniel',
            birth_date=date(2020, 11, 2),
            weight_kg=7.2,
            height_cm=33,
            description="Penelope is our sweet and nurturing matriarch. As a purebred Cavalier, she has a beautifully soft, tri-color coat and the most expressive eyes. She is incredibly affectionate and patient, making her an exceptional mother. Her puppies inherit her gentle nature and loving spirit.",
            main_image_s3_key=penelope_main_keys.get('original') if penelope_main_keys else None,
            main_image_s3_key_large=penelope_main_keys.get('large') if penelope_main_keys else None,
            alternate_image_s3_key_1=upload_seed_image('penelope-2.jpg', 'parents_alternates'),
            alternate_image_s3_key_2=upload_seed_image('penelope-3.jpg', 'parents_alternates')
        )

        # Buckeye
        buckeye_main_keys = upload_seed_image('buckeye.jpg', 'parents', create_responsive=True)
        parent_buckeye = Parent(
            name='Buckeye',
            role=ParentRole.DAD,
            breed='Merle Poodle',
            birth_date=date(2022, 1, 30),
            weight_kg=9.0,
            height_cm=40,
            description="Buckeye is our handsome and playful Merle Poodle. His unique coat turns heads everywhere he goes. He has a goofy, fun-loving personality but is also incredibly smart and eager to please. He brings beautiful color patterns and a joyful energy to his litters.",
            main_image_s3_key=buckeye_main_keys.get('original') if buckeye_main_keys else None,
            main_image_s3_key_large=buckeye_main_keys.get('large') if buckeye_main_keys else None,
            alternate_image_s3_key_1=upload_seed_image('buckeye-2.jpg', 'parents_alternates'),
            alternate_image_s3_key_2=upload_seed_image('IMG_8845.heic', 'parents_alternates')
        )

        # Minnie
        minnie_main_keys = upload_seed_image('minnie.jpg', 'parents', create_responsive=True)
        parent_minnie = Parent(
            name='Minnie',
            role=ParentRole.MOM,
            breed='Cavalier King Charles Spaniel',
            birth_date=date(2021, 8, 22),
            weight_kg=6.8,
            height_cm=31,
            description="Minnie is a delightful and spirited Cavalier with classic Blenheim markings. She is incredibly social and loves everyone she meets. As a mother, she is attentive and playful, raising confident and happy puppies. Her charming personality is simply irresistible.",
            main_image_s3_key=minnie_main_keys.get('original') if minnie_main_keys else None,
            main_image_s3_key_large=minnie_main_keys.get('large') if minnie_main_keys else None,
            alternate_image_s3_key_1=upload_seed_image('minnie-2.jpg', 'parents_alternates'),
            alternate_image_s3_key_2=upload_seed_image('minnie-3.jpg', 'parents_alternates')
        )

        db.session.add_all([parent_archie, parent_penelope, parent_buckeye, parent_minnie])
        db.session.commit()
        print("Parents created with full details and alternate images.")

        # --- Create Puppies and Assign to Parents ---
        
        # Litter 1: Archie & Penelope
        puppy_river = Puppy(name='River', birth_date=date(2024, 1, 15), status=PuppyStatus.AVAILABLE, dad_id=parent_archie.id, mom_id=parent_penelope.id, main_image_s3_key=upload_seed_image('river.jpg', 'puppies'))
        puppy_benson = Puppy(name='Benson', birth_date=date(2024, 1, 15), status=PuppyStatus.RESERVED, dad_id=parent_archie.id, mom_id=parent_penelope.id, main_image_s3_key=upload_seed_image('benson.jpg', 'puppies'))
        pup_ap_1 = Puppy(name='Coca', birth_date=date(2024, 1, 15), status=PuppyStatus.SOLD, dad_id=parent_archie.id, mom_id=parent_penelope.id, main_image_s3_key=upload_seed_image('penelope-archie-pup-1.jpg', 'puppies'))
        pup_ap_2 = Puppy(name='Spot', birth_date=date(2024, 1, 15), status=PuppyStatus.SOLD, dad_id=parent_archie.id, mom_id=parent_penelope.id, main_image_s3_key=upload_seed_image('penelope-archie-pup-2.jpg', 'puppies'))
        
        # Litter 2: Buckeye & Minnie
        pup_bm_1 = Puppy(name='Oreo', birth_date=date(2024, 2, 20), status=PuppyStatus.AVAILABLE, dad_id=parent_buckeye.id, mom_id=parent_minnie.id, main_image_s3_key=upload_seed_image('minnie-buckeye-pup-1.jpg', 'puppies'))
        
        # Litter 3: Buckeye & Penelope
        pup_bp_1 = Puppy(name='Patches', birth_date=date(2024, 3, 1), status=PuppyStatus.AVAILABLE, dad_id=parent_buckeye.id, mom_id=parent_penelope.id, main_image_s3_key=upload_seed_image('penelope-buckey-pup-1.jpg', 'puppies'))
        
        db.session.add_all([puppy_river, puppy_benson, pup_ap_1, pup_ap_2, pup_bm_1, pup_bp_1])
        print("Puppies created and assigned to parents.")

        # --- Final Touches: Reviews and Banners ---
        db.session.add(Review(author_name='The Smith Family', testimonial_text='We had an amazing experience from start to finish. Our puppy is healthy, well-socialized, and the perfect addition to our family. We couldn''t be happier!', is_featured=True))

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