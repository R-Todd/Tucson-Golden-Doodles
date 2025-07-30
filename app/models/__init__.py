# app/models/__init__.py

from flask_sqlalchemy import SQLAlchemy

# Initialize the database instance.
db = SQLAlchemy()

# Import models and enums into this namespace so they can be
# accessed from `app.models` elsewhere in the application.
from .enums import ParentRole, PuppyStatus
# --- VERIFY THIS LINE INCLUDES AnnouncementBanner ---
from .site_models import SiteMeta, HeroSection, AboutSection, GalleryImage, AnnouncementBanner
from .parent_models import Parent, ParentImage
from .puppy_models import Puppy
from .review_models import Review
from .user_models import User