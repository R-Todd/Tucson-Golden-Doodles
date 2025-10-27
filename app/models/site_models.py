# app/models/site_models.py
"""
Defines various models for managing site-wide content and configuration.

These models are typically for content that is edited by an admin and displayed
on various pages of the public-facing website, such as the homepage hero,
about section, gallery, and contact information.
"""

from . import db
from .puppy_models import Puppy  # Import Puppy to define relationship

# Change the class name from SiteMeta to SiteDetails.
class SiteDetails(db.Model):
    """
    Stores site-wide details and contact information.

    This table is intended to have only a single row, acting as a central
    configuration point for details like phone number, email, and social media links
    that may appear in multiple places (e.g., header, footer).
    """
    # The table name is explicitly set to 'site_details' for clarity.
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
    # S3 key for the full-resolution gallery image.
    image_s3_key = db.Column(db.String(255), nullable=False)
    caption = db.Column(db.String(255))
    # Used to control the display order of images in the gallery.
    sort_order = db.Column(db.Integer, default=0)

    def __repr__(self):
        """Provides a developer-friendly representation of the GalleryImage object."""
        return f'<GalleryImage {self.id}>'


class AnnouncementBanner(db.Model):
    """
    Manages the content for a site-wide announcement banner.

    This is typically used to highlight new litters or important news. It can
    optionally be linked to a specific puppy to create a direct call-to-action.
    Intended to have only one active banner at a time.
    """
    id = db.Column(db.Integer, primary_key=True)
    # Controls whether the banner is currently displayed on the site.
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    main_text = db.Column(db.String(200), default=" Check out our newest litter! ")
    sub_text = db.Column(db.String(300), default="A beautiful new litter from {mom_name} & {dad_name}.")
    button_text = db.Column(db.String(50), default="Meet the Puppies")

    # An optional foreign key to link the banner to one specific puppy,
    # allowing the call-to-action button to lead to a puppy's detail page.
    featured_puppy_id = db.Column(db.Integer, db.ForeignKey('puppy.id'), nullable=True)
    
    # The relationship to the Puppy model, allowing easy access to the
    # featured_puppy object from a banner instance.
    featured_puppy = db.relationship('Puppy', foreign_keys=[featured_puppy_id])

    def __repr__(self):
        """Provides a developer-friendly representation of the AnnouncementBanner object."""
        return f'<AnnouncementBanner {self.id}>'

# --- NEW MODEL ADDED HERE ---
class ParentsPageHeader(db.Model):
    """
    Manages the content for the header section on the 'Our Parents' page.
    Intended for a single row of data.
    """
    __tablename__ = 'parents_page_header' # Explicit table name
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), default="Our Doodle Parents")
    tagline = db.Column(db.String(300), default="Healthy Puppies Start with Exceptional Parents")
    
    # Store the list points as a single text block, separated by newlines.
    # Each point will have a title and description, separated by a pipe '|'.
    # Example: "Health Tested|DNA, OFA screenings..."
    description_points = db.Column(db.Text, default=(
        "Health Tested|DNA, OFA, and PennHIP screenings for hips, elbows, heart, and eyes.\n"
        "Great Temperament|Parents chosen for friendliness, intelligence, and adaptability.\n"
        "Strong Structure|Balanced build for lifelong health and mobility.\n"
        "Ethical Breeding|Planned pairings, early socialization, and loving care.\n"
        "Family & Therapy Ready|Confident, happy puppies prepared for their forever homes."
    ))
    
    # S3 key for the header image.
    image_s3_key = db.Column(db.String(255))

    def __repr__(self):
        """Provides a developer-friendly representation."""
        return f'<ParentsPageHeader {self.id}>'

    # Helper property to easily parse the description points in the template
    @property
    def points_list(self):
        """ Parses the description_points text into a list of (title, description) tuples. """
        points = []
        if self.description_points:
            lines = self.description_points.strip().split('\n')
            for line in lines:
                parts = line.split('|', 1)
                if len(parts) == 2:
                    points.append((parts[0].strip(), parts[1].strip()))
                elif len(parts) == 1: # Handle lines with only a title (no pipe)
                    points.append((parts[0].strip(), "")) 
        return points