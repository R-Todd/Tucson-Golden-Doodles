# app/models/__init__.py

from flask_sqlalchemy import SQLAlchemy

# Initialize the database instance.
# This is the central point for the db object, which will be imported by models.
db = SQLAlchemy()

# Import models and enums into this namespace so they can be
# accessed from `app.models` elsewhere in the application.
# This makes the refactoring transparent to other parts of the app.
from .enums import ParentRole, PuppyStatus
# --- ADD AnnouncementBanner TO THIS LINE ---
from .site_models import SiteMeta, HeroSection, AboutSection, GalleryImage, AnnouncementBanner
from .parent_models import Parent, ParentImage
from .puppy_models import Puppy
from .review_models import Review
from .user_models import User