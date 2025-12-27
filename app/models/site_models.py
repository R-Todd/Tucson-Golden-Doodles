# app/models/site_models.py
from . import db

class SiteDetails(db.Model):
    __tablename__ = 'site_details'
    id = db.Column(db.Integer, primary_key=True)
    phone_number = db.Column(db.String(20))
    email = db.Column(db.String(120))
    social_facebook_url = db.Column(db.String(255))
    social_instagram_url = db.Column(db.String(255))

class HeroSection(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    main_title = db.Column(db.String(200), default="Copper Skye Doodles")
    subtitle = db.Column(db.String(200), default="Established 2013")
    description = db.Column(db.String(300), default="Tucson Goldendoodles, Bernedoodles & Golden Mountain Doodles")
    image_s3_key = db.Column(db.String(255))

class AboutSection(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200))
    content_html = db.Column(db.Text)
    image_s3_key = db.Column(db.String(255))

class GalleryImage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    image_s3_key = db.Column(db.String(255), nullable=False)
    caption = db.Column(db.String(255))
    sort_order = db.Column(db.Integer, default=0)

class AnnouncementBanner(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    main_text = db.Column(db.String(200), default=" Check out our newest litter! ")
    sub_text = db.Column(db.String(300), default="A beautiful new litter from {mom_name} & {dad_name}.")
    button_text = db.Column(db.String(50), default="Meet the Puppies")
    featured_puppy_id = db.Column(db.Integer, db.ForeignKey('puppy.id'), nullable=True)
    featured_puppy = db.relationship('Puppy', foreign_keys=[featured_puppy_id])