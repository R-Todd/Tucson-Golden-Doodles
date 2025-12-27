# app/routes/admin/routes.py

from flask import redirect, url_for, request, render_template
from flask_login import current_user, login_user, logout_user
from flask_admin.menu import MenuLink

from app import db
from app.models import (
    User, Parent, Litter, Puppy, Review, HeroSection, AboutSection, GalleryImage, AnnouncementBanner
)
from . import bp, admin
from .views import (
    ParentAdminView, PuppyAdminView, LitterAdminView, HeroSectionAdminView,
    AboutSectionAdminView, AnnouncementBannerAdminView, ReviewAdminView, AdminModelView, GalleryImageAdminView
)

# --- Parent Management ---
admin.add_view(ParentAdminView(Parent, db.session))

# --- Puppy & Litter Management ---
# Registering these under the "Puppies" category creates a dropdown menu in the sidebar
admin.add_view(LitterAdminView(Litter, db.session, name="Manage Litters", category="Puppies"))
admin.add_view(PuppyAdminView(Puppy, db.session, name="Individual Puppies", category="Puppies"))

# --- Site Content Management ---
admin.add_view(ReviewAdminView(Review, db.session))
admin.add_view(HeroSectionAdminView(HeroSection, db.session, name="Hero Section"))
admin.add_view(AboutSectionAdminView(AboutSection, db.session, name="About Section"))
admin.add_view(AnnouncementBannerAdminView(AnnouncementBanner, db.session, name="Announcement Banner"))
admin.add_view(GalleryImageAdminView(GalleryImage, db.session, name="Gallery Images"))

# --- Navigation Links ---
admin.add_link(MenuLink(name='Logout', category='', url='/admin/logout'))

# Authentication routes for admin login and logout ---------------------
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