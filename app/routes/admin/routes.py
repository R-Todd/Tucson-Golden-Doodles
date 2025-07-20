# app/routes/admin/routes.py

from flask import redirect, url_for, request, render_template
from flask_login import current_user, login_user, logout_user

from app import db
from app.models import (
    User, Parent, Puppy, Review, HeroSection, AboutSection, GalleryImage
)
# --- Key Change ---
# Import the blueprint 'bp' and the 'admin' object from this package's __init__.py.
# This is the core of the fix. We are now using the objects that were
# centrally created, rather than creating new ones.
from . import bp, admin

# Import the separated view classes from .views
from .views import (
    AdminModelView, ParentAdminView, PuppyAdminView, HeroSectionAdminView,
    AboutSectionAdminView
)

# --- Model View Registration ---
# This section no longer defines 'admin'. It *uses* the imported 'admin' object
# to register the views for each of your database models.
admin.add_view(ParentAdminView(Parent, db.session))
admin.add_view(PuppyAdminView(Puppy, db.session))
admin.add_view(AdminModelView(Review, db.session))
admin.add_view(HeroSectionAdminView(HeroSection, db.session, name="Hero Section"))
admin.add_view(AboutSectionAdminView(AboutSection, db.session, name="About Section"))
admin.add_view(AdminModelView(GalleryImage, db.session, name="Gallery Images"))


# --- Route Registration ---
# These routes are registered with the 'bp' blueprint, which is also
# imported from the __init__.py file.
@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('admin.index'))
    if request.method == 'POST':
        user = User.query.filter_by(username=request.form['username']).first()
        if user is None or not user.check_password(request.form['password']):
            return 'Invalid username or password'
        login_user(user)
        # Redirect to the main admin dashboard after successful login
        return redirect(url_for('admin.index'))
    return render_template('login.html')

@bp.route('/logout')
def logout():
    logout_user()
    # Redirect to the public homepage after logout
    return redirect(url_for('main.index'))