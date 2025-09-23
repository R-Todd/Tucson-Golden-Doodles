# app/routes/admin/routes.py

from flask import redirect, url_for, request, render_template
from flask_login import current_user, login_user, logout_user
from flask_admin.menu import MenuLink

from app import db
from app.models import (
    User, Parent, Puppy, Review, HeroSection, AboutSection, GalleryImage, AnnouncementBanner, Breed
)
from . import bp, admin
from .views import (
    ParentAdminView, PuppyAdminView, HeroSectionAdminView,
    AboutSectionAdminView, AnnouncementBannerAdminView, ReviewAdminView, AdminModelView, GalleryImageAdminView
)
# --- THIS IS THE NEW IMPORT ---
from .views.breed_views import BreedAdminView

# Register admin views for different models
admin.add_view(ParentAdminView(Parent, db.session))
admin.add_view(PuppyAdminView(Puppy, db.session))

# --- THIS LINE IS CHANGED ---
# It now uses our custom BreedAdminView.
admin.add_view(BreedAdminView(Breed, db.session))

# Register admin views for site content using Bootstrap 5 templates
admin.add_view(ReviewAdminView(Review, db.session))
admin.add_view(HeroSectionAdminView(HeroSection, db.session, name="Hero Section"))
admin.add_view(AboutSectionAdminView(AboutSection, db.session, name="About Section"))
admin.add_view(AnnouncementBannerAdminView(AnnouncementBanner, db.session, name="Announcement Banner"))
admin.add_view(GalleryImageAdminView(GalleryImage, db.session, name="Gallery Images"))

# Add a logout link to the admin menu
admin.add_link(MenuLink(name='Logout', category='', url='/admin/logout'))


# Define authentication routes for admin login and logout
@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('admin.index'))
    if request.method == 'POST':
        user = User.query.filter_by(username=request.form['username']).first()
        if user is None or not user.check_password(request.form['password']):
            return 'Invalid username or password'
        login_user(user)
        return redirect(url_for('admin.index'))
    return render_template('login.html')

@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.index'))