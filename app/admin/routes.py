from flask import redirect, url_for, request, render_template
from flask_admin import Admin, AdminIndexView, expose
from flask_admin.contrib.sqla import ModelView
from flask_login import current_user, login_user, logout_user
from wtforms.fields import SelectField

from app import db
from app.models import User, Parent, Puppy, Review, HeroSection, AboutSection, GalleryImage, ParentRole
from . import bp

class MyAdminIndexView(AdminIndexView):
    @expose('/')
    def index(self):
        if not current_user.is_authenticated:
            return redirect(url_for('admin_auth.login'))
        return super(MyAdminIndexView, self).index()

admin = Admin(name='Tucson Golden Doodles Admin', template_mode='bootstrap3', index_view=MyAdminIndexView())

class AdminModelView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('admin_auth.login', next=request.url))

# Final custom view for the Parent model
class ParentAdminView(AdminModelView):
    # Use form_overrides to force a SelectField
    form_overrides = {
        'role': SelectField
    }
    
    # Use form_args to configure the SelectField
    form_args = {
        'role': {
            'label': 'Role',
            # Generate choices dynamically from the ParentRole enum
            'choices': [(role.name, role.value) for role in ParentRole],
            # This is the key change: handle both string and enum inputs
            'coerce': lambda x: ParentRole[x] if isinstance(x, str) else x
        }
    }

# Add views for your models, using the custom view for Parents
admin.add_view(ParentAdminView(Parent, db.session))
admin.add_view(AdminModelView(Puppy, db.session))
admin.add_view(AdminModelView(Review, db.session))
admin.add_view(AdminModelView(HeroSection, db.session))
admin.add_view(AdminModelView(AboutSection, db.session))
admin.add_view(AdminModelView(GalleryImage, db.session))

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