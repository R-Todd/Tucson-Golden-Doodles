# app/routes/admin/routes.py

from flask import redirect, url_for, request, render_template
from flask_login import current_user, login_user, logout_user

from app import db
from app.models import (
    User, Parent, Puppy, Review, HeroSection, AboutSection, GalleryImage
)
# --- Blueprint and Admin Object ---
# Import the centrally created 'bp' (for routing) and 'admin' (for views)
# objects from this package's __init__.py file.
from . import bp, admin

# --- View Imports ---
# Import the custom ModelView classes from the neighboring 'views.py' file.
from .views import (
    AdminModelView, ParentAdminView, PuppyAdminView, HeroSectionAdminView,
    AboutSectionAdminView
)

# === View Registration ===
# This section registers each ModelView with the central 'admin' object.
# Each line makes a model available for CRUD operations in the admin interface.
# --------------------------------------------------------------------------
admin.add_view(ParentAdminView(Parent, db.session))
admin.add_view(PuppyAdminView(Puppy, db.session))
admin.add_view(AdminModelView(Review, db.session))
admin.add_view(HeroSectionAdminView(HeroSection, db.session, name="Hero Section"))
admin.add_view(AboutSectionAdminView(AboutSection, db.session, name="About Section"))
admin.add_view(AdminModelView(GalleryImage, db.session, name="Gallery Images"))


# === Authentication Route Definitions ===
# These routes handle the process of logging users in and out of the admin panel.
# They are registered with the 'bp' blueprint.
# --------------------------------------------------------------------------
@bp.route('/login', methods=['GET', 'POST'])
def login():
    """Handles admin user login."""
    # If user is already logged in, redirect them to the admin dashboard.
    if current_user.is_authenticated:
        return redirect(url_for('admin.index'))

    if request.method == 'POST':
        # Find the user by username.
        user = User.query.filter_by(username=request.form['username']).first()
        # Validate the user's password.
        if user is None or not user.check_password(request.form['password']):
            return 'Invalid username or password' # Consider flashing a message instead.
        
        # Log the user in and redirect to the admin dashboard.
        login_user(user)
        return redirect(url_for('admin.index'))
    
    # For a GET request, show the login page.
    return render_template('login.html')

@bp.route('/logout')
def logout():
    """Handles admin user logout."""
    logout_user()
    # Redirect to the public homepage after logout.
    return redirect(url_for('main.index'))