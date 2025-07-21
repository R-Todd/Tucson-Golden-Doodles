# app/routes/admin/routes.py

from flask import redirect, url_for, request, render_template
from flask_login import current_user, login_user, logout_user
# Import MenuLink
from flask_admin.menu import MenuLink

from app import db
from app.models import (
    User, Parent, Puppy, Review, HeroSection, AboutSection, GalleryImage
)
from . import bp, admin
from .views import (
    AdminModelView, ParentAdminView, PuppyAdminView, HeroSectionAdminView,
    AboutSectionAdminView
)

# === View Registration ===
admin.add_view(ParentAdminView(Parent, db.session))
admin.add_view(PuppyAdminView(Puppy, db.session))
admin.add_view(AdminModelView(Review, db.session))
admin.add_view(HeroSectionAdminView(HeroSection, db.session, name="Hero Section"))
admin.add_view(AboutSectionAdminView(AboutSection, db.session, name="About Section"))
admin.add_view(AdminModelView(GalleryImage, db.session, name="Gallery Images"))

# This adds a dedicated "Logout" link to the main admin navigation bar.
admin.add_link(MenuLink(name='Logout', category='', url='/admin/logout'))


# === Authentication Route Definitions ===
@bp.route('/login', methods=['GET', 'POST'])
def login():
    """Handles admin user login."""
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
    """Handles admin user logout."""
    logout_user()
    return redirect(url_for('main.index'))