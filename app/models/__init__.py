# app/models/__init__.py
"""
Initializes the database connection and aggregates all model definitions.

This package initializer creates the SQLAlchemy instance (`db`) that all models
will use. It also imports all model classes and enums into the `app.models`
namespace, providing a single, consistent point of access for other parts of
the application (e.g., `from app.models import User, Puppy`).
"""

from flask_sqlalchemy import SQLAlchemy

# Initialize the database instance.
db = SQLAlchemy()

# Import enums and all model classes
from .enums import ParentRole, PuppyStatus
from .site_models import SiteDetails, HeroSection, AboutSection, GalleryImage, AnnouncementBanner 
from .parent_models import Parent, ParentImage
from .puppy_models import Puppy
from .review_models import Review
from .user_models import User