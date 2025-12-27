# app/models/site_models.py
"""
Defines various models for managing site-wide content and configuration.
"""

from . import db

class SiteDetails(db.Model):
    """
    Stores site-wide details and contact information.
    """
    __tablename__ = 'site_details'
    
    id = db.Column(db.Integer, primary_key=True)
    phone_number = db.Column(db.String(20))
    email = db.Column(db.String(120))
    social_facebook_url = db.Column(db.String(255))
    social_instagram_url = db.Column(db.String(255))

    def __repr__(self):
        return f'<SiteDetails {self.id}>'

class HeroSection(db.Model):
    """
    Manages the content for the homepage's main hero section.
    """
    id = db.Column(db.Integer, primary_key=True)
    main_title = db.Column(db.String(200), default="Copper Skye Doodles")
    subtitle = db.Column(db.String(200), default="Established 2001")
    description = db.Column(db.String(300), default="Arizona Goldendoodles, Bernedoodles & Golden Mountain Doodles")
    scroll_text_main = db.Column(db.String(100), default="Website Updated")
    scroll_text_secondary = db.Column(db.String(100), default="See Available Puppies Below")

    image_s3_key = db.Column(db.String(255))
    image_s3_key_small = db.Column(db.String(255))
    image_s3_key_medium = db.Column(db.String(255))
    image_s3_key_large = db.Column(db.String(255))

    def __repr__(self):
        return f'<HeroSection {self.main_title}>'

class AboutSection(db.Model):
    """
    Manages the content for the 'About Us' section on the homepage.
    """
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200))
    content_html = db.Column(db.Text)

    image_s3_key = db.Column(db.String(255))
    image_s3_key_small = db.Column(db.String(255))
    image_s3_key_medium = db.Column(db.String(255))
    image_s3_key_large = db.Column(db.String(255))

    def __repr__(self):
        return f'<AboutSection {self.title}>'

class GalleryImage(db.Model):
    """
    Represents a single image in the main site gallery.
    """
    id = db.Column(db.Integer, primary_key=True)
    image_s3_key = db.Column(db.String(255), nullable=False)
    caption = db.Column(db.String(255))
    sort_order = db.Column(db.Integer, default=0)

    def __repr__(self):
        return f'<GalleryImage {self.id}>'

class AnnouncementBanner(db.Model):
    """
    Manages the content for a site-wide announcement banner.
    Now updated to support the Litter model structure.
    """
    id = db.Column(db.Integer, primary_key=True)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    main_text = db.Column(db.String(200), default=" Check out our newest litter! ")
    
    # Note: sub_text should now use {mom_name} and {dad_name} which will be 
    # pulled from puppy.litter.mom and puppy.litter.dad in the view logic.
    sub_text = db.Column(db.String(300), default="A beautiful new litter from {mom_name} & {dad_name}.")
    button_text = db.Column(db.String(50), default="Meet the Puppies")

    featured_puppy_id = db.Column(db.Integer, db.ForeignKey('puppy.id'), nullable=True)
    
    # Relationship to the Puppy model
    featured_puppy = db.relationship('Puppy', foreign_keys=[featured_puppy_id])

    def __repr__(self):
        return f'<AnnouncementBanner {self.id}>'