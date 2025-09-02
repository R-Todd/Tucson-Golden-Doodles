# app/models/user_models.py
"""
Defines the User model for authentication and user management.
"""

from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from . import db

class User(UserMixin, db.Model):
    """
    Represents an administrative user in the system.

    This model integrates with Flask-Login (`UserMixin`) to provide session
    management for authenticated users. Tp storee credentials securely.
    """
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    # Password hash storage. Length is increased for security
    password_hash = db.Column(db.String(256)) 

    def set_password(self, password):
        """Hashes the given password and stores it."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Verifies a given password against the stored hash."""
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        """Provides a developer-friendly representation of the User object."""
        return f'<User {self.username}>'