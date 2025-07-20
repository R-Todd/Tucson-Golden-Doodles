from flask import redirect, url_for, request, render_template
from flask_admin import Admin, AdminIndexView, expose
from flask_login import current_user, login_user, logout_user

from app import db
from app.models import (
    User, Parent, Puppy, Review, HeroSection, AboutSection, GalleryImage
)
from . import bp
# Import the separated view classes
from .views import (
    AdminModelView, ParentAdminView, PuppyAdminView, HeroSectionAdminView,
    AboutSectionAdminView
)

class MyAdminIndexView(AdminIndexView):
    @expose('/')
    def index(self):
        if not current_user.is_authenticated:
            return redirect(url_for('admin_auth.login'))
        return super(MyAdminIndexView, self).index()

# This is the section to update
admin = Admin(
    name='Tucson Golden Doodles Admin',
    template_mode='bootstrap3',
    index_view=MyAdminIndexView(),
    base_template='admin/base_admin.html'  # Use your new file name here
)

# Add views for your models, using the imported view classes
admin.add_view(ParentAdminView(Parent, db.session))
admin.add_view(PuppyAdminView(Puppy, db.session))
admin.add_view(AdminModelView(Review, db.session))
admin.add_view(HeroSectionAdminView(HeroSection, db.session, name="Hero Section"))
admin.add_view(AboutSectionAdminView(AboutSection, db.session, name="About Section"))
admin.add_view(AdminModelView(GalleryImage, db.session, name="Gallery Images"))


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