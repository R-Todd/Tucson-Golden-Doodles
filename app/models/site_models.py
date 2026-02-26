# app/models/site_models.py
"""
Defines various models for managing site-wide content and configuration.

These models are typically for content that is edited by an admin and displayed
on various pages of the public-facing website, such as the homepage hero,
about section, gallery, and contact information.
"""

from . import db


class SiteDetails(db.Model):
    """
    Stores site-wide details and contact information.

    This table is intended to have only a single row, acting as a central
    configuration point for details like phone number, email, and social media links
    that may appear in multiple places (e.g., header, footer).
    """
    __tablename__ = 'site_details'

    id = db.Column(db.Integer, primary_key=True)
    phone_number = db.Column(db.String(20))
    email = db.Column(db.String(120))
    social_facebook_url = db.Column(db.String(255))
    social_instagram_url = db.Column(db.String(255))

    def __repr__(self):
        """Provides a developer-friendly representation of the SiteDetails object."""
        return f'<SiteDetails {self.id}>'


class HeroSection(db.Model):
    """
    Manages the content for the homepage's main hero section.

    Intended for a single row of data to control the main title, subtitle,
    description, and background images of the hero banner.
    """
    id = db.Column(db.Integer, primary_key=True)
    main_title = db.Column(db.String(200), default="Copper Skye Doodles")
    subtitle = db.Column(db.String(200), default="Established 2001")
    description = db.Column(db.String(300), default="Arizona Goldendoodles, Bernedoodles & Golden Mountain Doodles")
    scroll_text_main = db.Column(db.String(100), default="Website Updated")
    scroll_text_secondary = db.Column(db.String(100), default="See Available Puppies Below")

    # S3 keys for the hero background image, with responsive sizes.
    image_s3_key = db.Column(db.String(255))
    image_s3_key_small = db.Column(db.String(255))
    image_s3_key_medium = db.Column(db.String(255))
    image_s3_key_large = db.Column(db.String(255))

    def __repr__(self):
        """Provides a developer-friendly representation of the HeroSection object."""
        return f'<HeroSection {self.main_title}>'


class AboutSection(db.Model):
    """
    Manages the content for the 'About Us' section on the homepage.

    Intended for a single row of data to control the title, text content (HTML),
    and associated image for this section.
    """
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200))
    content_html = db.Column(db.Text)

    # S3 keys for the section's image, with responsive sizes.
    image_s3_key = db.Column(db.String(255))
    image_s3_key_small = db.Column(db.String(255))
    image_s3_key_medium = db.Column(db.String(255))
    image_s3_key_large = db.Column(db.String(255))

    def __repr__(self):
        """Provides a developer-friendly representation of the AboutSection object."""
        return f'<AboutSection {self.title}>'


class GalleryImage(db.Model):
    """
    Represents a single image in the main site gallery.

    This is for a general-purpose photo gallery, separate from the images
    associated with specific parents or puppies.
    """
    id = db.Column(db.Integer, primary_key=True)
    image_s3_key = db.Column(db.String(255), nullable=False)
    caption = db.Column(db.String(255))
    sort_order = db.Column(db.Integer, default=0)

    def __repr__(self):
        """Provides a developer-friendly representation of the GalleryImage object."""
        return f'<GalleryImage {self.id}>'


class AnnouncementBanner(db.Model):
    """
    Manages the content for a site-wide announcement banner.

    Now linked to a Litter (not a Puppy). The CTA should lead to the litter section
    on the puppies page.
    Intended to have only one active banner at a time.
    """
    id = db.Column(db.Integer, primary_key=True)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    main_text = db.Column(db.String(200), default=" Check out our newest litter! ")
    sub_text = db.Column(db.String(300), default="A beautiful new litter from {mom_name} & {dad_name}.")
    button_text = db.Column(db.String(50), default="Meet the Puppies")

    # NEW: Link banner to a specific litter (optional)
    featured_litter_id = db.Column(db.Integer, db.ForeignKey('litter.id'), nullable=True)

    # Relationship to Litter (string reference avoids circular imports)
    featured_litter = db.relationship('Litter', foreign_keys=[featured_litter_id])

    def __repr__(self):
        """Provides a developer-friendly representation of the AnnouncementBanner object."""
        return f'<AnnouncementBanner {self.id}>'


class ParentsPageIntro(db.Model):
    """
    Manages the main image and introductory text for the Parents page.

    Intended for a single row of data to control a top-of-page feature image
    and an editable description/intro block displayed above the Moms/Dads grids.
    """

    id = db.Column(db.Integer, primary_key=True)
    is_active = db.Column(db.Boolean, default=True, nullable=False)

    title = db.Column(db.String(200), default="Our Parents")
    content_html = db.Column(db.Text)

    # S3 keys for the page's main image, with responsive sizes.
    image_s3_key = db.Column(db.String(255))
    image_s3_key_small = db.Column(db.String(255))
    image_s3_key_medium = db.Column(db.String(255))
    image_s3_key_large = db.Column(db.String(255))

    def __repr__(self):
        """Provides a developer-friendly representation of the ParentsPageIntro object."""
        return f'<ParentsPageIntro {self.title}>'