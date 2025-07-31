# app/models/site_models.py

from . import db
from .puppy_models import Puppy  # Import Puppy to define relationship

# Site-wide metadata, intended for a single row of data
class SiteMeta(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    phone_number = db.Column(db.String(20))
    email = db.Column(db.String(120))
    social_facebook_url = db.Column(db.String(255))
    social_instagram_url = db.Column(db.String(255))

    def __repr__(self):
        return f'<SiteMeta {self.id}>'

# --- Homepage Content Models ---

class HeroSection(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    image_url = db.Column(db.String(255))
    image_url_small = db.Column(db.String(255))
    image_url_medium = db.Column(db.String(255))
    image_url_large = db.Column(db.String(255))
    main_title = db.Column(db.String(200), default="Copper Skye Doodles")
    subtitle = db.Column(db.String(200), default="Established 2001")
    description = db.Column(db.String(300), default="Arizona Goldendoodles, Bernedoodles & Golden Mountain Doodles")
    scroll_text_main = db.Column(db.String(100), default="Website Updated")
    scroll_text_secondary = db.Column(db.String(100), default="See Available Puppies Below")


    def __repr__(self):
        return f'<HeroSection {self.main_title}>'

class AboutSection(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200))
    content_html = db.Column(db.Text)
    image_url = db.Column(db.String(255))
    image_url_small = db.Column(db.String(255))
    image_url_medium = db.Column(db.String(255))
    image_url_large = db.Column(db.String(255))


    def __repr__(self):
        return f'<AboutSection {self.title}>'

class GalleryImage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    image_url = db.Column(db.String(255), nullable=False)
    caption = db.Column(db.String(255))
    sort_order = db.Column(db.Integer, default=0)

    def __repr__(self):
        return f'<GalleryImage {self.id}>'


# --- MODIFIED: AnnouncementBanner now links to a Puppy ---
class AnnouncementBanner(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    main_text = db.Column(db.String(200), default="✨ Check out our newest litter! ✨")
    sub_text = db.Column(db.String(300), default="A beautiful new litter from {mom_name} & {dad_name}.")
    button_text = db.Column(db.String(50), default="Meet the Puppies")

    # This foreign key will link the banner to one specific puppy.
    featured_puppy_id = db.Column(db.Integer, db.ForeignKey('puppy.id'), nullable=True)
    
    # Define the relationship to the Puppy model
    featured_puppy = db.relationship('Puppy', foreign_keys=[featured_puppy_id])

    def __repr__(self):
        return f'<AnnouncementBanner {self.id}>'