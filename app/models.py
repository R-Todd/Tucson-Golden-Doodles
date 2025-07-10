from . import db
import enum

# Enum for Parent roles to ensure data consistency
class ParentRole(enum.Enum):
    DAD = "Dad"
    MOM = "Mom"

# Enum for Puppy status
class PuppyStatus(enum.Enum):
    AVAILABLE = "Available"
    RESERVED = "Reserved"
    SOLD = "Sold"

# Site-wide metadata, intended for a single row of data
class SiteMeta(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    phone_number = db.Column(db.String(20))
    email = db.Column(db.String(120))
    social_facebook_url = db.Column(db.String(255))
    social_instagram_url = db.Column(db.String(255))

    def __repr__(self):
        return f'<SiteMeta {self.id}>'

# Parent dogs (Sires and Dams)
class Parent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    role = db.Column(db.Enum(ParentRole), nullable=False) # e.g., ParentRole.DAD
    breed = db.Column(db.String(100))
    birth_date = db.Column(db.Date)
    weight_kg = db.Column(db.Float)
    height_cm = db.Column(db.Float)
    description = db.Column(db.Text)
    main_image_url = db.Column(db.String(255))
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    
    # One-to-many relationship to ParentImage
    images = db.relationship('ParentImage', backref='parent', lazy=True, cascade="all, delete-orphan")
    
    # Relationships to Puppy, distinguishing between dad and mom roles
    litters_as_dad = db.relationship('Puppy', foreign_keys='Puppy.dad_id', backref='dad', lazy='dynamic')
    litters_as_mom = db.relationship('Puppy', foreign_keys='Puppy.mom_id', backref='mom', lazy='dynamic')

    @property
    def litters(self):
        """Returns a query for all puppies from this parent, based on role."""
        if self.role == ParentRole.DAD:
            return self.litters_as_dad
        else:
            return self.litters_as_mom

    @property
    def grouped_litters(self):
        """
        Groups this parent's puppies by litter, ordered by date.
        A litter is defined by the birth date and parents.
        Returns an ordered dictionary where keys are a tuple of (birth_date, dad, mom)
        and values are the list of puppies in that litter.
        """
        from collections import OrderedDict
        from itertools import groupby

        puppies = self.litters.order_by(Puppy.birth_date.desc(), Puppy.name).all()
        keyfunc = lambda p: (p.birth_date, p.dad, p.mom)
        return OrderedDict((k, list(g)) for k, g in groupby(puppies, keyfunc))

    def __repr__(self):
        return f'<Parent {self.name}>'

# Gallery images for parents
class ParentImage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    parent_id = db.Column(db.Integer, db.ForeignKey('parent.id'), nullable=False)
    image_url = db.Column(db.String(255), nullable=False)
    caption = db.Column(db.String(255))

    def __repr__(self):
        return f'<ParentImage {self.id} for Parent {self.parent_id}>'

# Puppies from litters
class Puppy(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100)) # e.g., "Blue Collar Male"
    birth_date = db.Column(db.Date, nullable=False)
    status = db.Column(db.Enum(PuppyStatus), nullable=False, default=PuppyStatus.AVAILABLE)
    dad_id = db.Column(db.Integer, db.ForeignKey('parent.id'), nullable=False)
    mom_id = db.Column(db.Integer, db.ForeignKey('parent.id'), nullable=False)
    main_image_url = db.Column(db.String(255))

    def __repr__(self):
        return f'<Puppy {self.id} ({self.name})>'

# Customer reviews
class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    author_name = db.Column(db.String(100), nullable=False)
    testimonial_text = db.Column(db.Text, nullable=False)
    is_featured = db.Column(db.Boolean, default=False, nullable=False)

    def __repr__(self):
        return f'<Review by {self.author_name}>'

# --- Homepage Content Models ---

class HeroSection(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    image_url = db.Column(db.String(255))
    title = db.Column(db.String(200))
    subtitle = db.Column(db.String(300))
    cta_text = db.Column(db.String(50))
    cta_link = db.Column(db.String(255))

    def __repr__(self):
        return f'<HeroSection {self.title}>'

class AboutSection(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200))
    content_html = db.Column(db.Text)
    image_url = db.Column(db.String(255))

    def __repr__(self):
        return f'<AboutSection {self.title}>'

class GalleryImage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    image_url = db.Column(db.String(255), nullable=False)
    caption = db.Column(db.String(255))
    sort_order = db.Column(db.Integer, default=0)

    def __repr__(self):
        return f'<GalleryImage {self.id}>'