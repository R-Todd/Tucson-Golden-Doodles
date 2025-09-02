# app/routes/admin/routes.py

from flask import redirect, url_for, request, render_template
from flask_login import current_user, login_user, logout_user
from flask_admin.menu import MenuLink

from app import db
from app.models import (
    User, Parent, Puppy, Review, HeroSection, AboutSection, GalleryImage, AnnouncementBanner
)
from . import bp, admin
from .views import (
    ParentAdminView, PuppyAdminView, HeroSectionAdminView,
    AboutSectionAdminView, AnnouncementBannerAdminView, ReviewAdminView, AdminModelView, GalleryImageAdminView
)

# Register admin views for different models
admin.add_view(ParentAdminView(Parent, db.session))
admin.add_view(PuppyAdminView(Puppy, db.session))

# Register admin views for site content using Bootstrap 5 templates
admin.add_view(ReviewAdminView(Review, db.session))
# Custom name for HeroSection view in the admin interface
admin.add_view(HeroSectionAdminView(HeroSection, db.session, name="Hero Section"))
# Custom name for AboutSection view in the admin interface
admin.add_view(AboutSectionAdminView(AboutSection, db.session, name="About Section"))
# Custom name for AnnouncementBanner view in the admin interface
admin.add_view(AnnouncementBannerAdminView(AnnouncementBanner, db.session, name="Announcement Banner"))
# Custom name for GalleryImage view in the admin interface
admin.add_view(GalleryImageAdminView(GalleryImage, db.session, name="Gallery Images"))

# Add a logout link to the admin menu
admin.add_link(MenuLink(name='Logout', category='', url='/admin/logout'))


# Define authentication routes for admin login and logout --------------------- CODE REVIEW
@bp.route('/login', methods=['GET', 'POST'])
def login():
    # If the user is already authenticated, redirect to the admin index page
    if current_user.is_authenticated:
        return redirect(url_for('admin.index'))
    # Handle POST request for login
    if request.method == 'POST':
        # Query the user by username
        user = User.query.filter_by(username=request.form['username']).first()
        # Check if user exists and password is correct
        if user is None or not user.check_password(request.form['password']):
            return 'Invalid username or password'
        # Log the user in
        login_user(user)
        return redirect(url_for('admin.index'))
    return render_template('login.html')

@bp.route('/logout')
def logout():
    # Log the user out
    logout_user()
    return redirect(url_for('main.index'))