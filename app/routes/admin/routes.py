from flask import redirect, url_for, request, render_template
from flask_admin import Admin, AdminIndexView, expose
from flask_admin.contrib.sqla import ModelView
from flask_login import current_user, login_user, logout_user
from wtforms.fields import SelectField

from app import db
from app.models import (
    User, Parent, Puppy, Review, HeroSection, AboutSection, GalleryImage, 
    ParentRole, PuppyStatus
)
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

# Custom view for the Parent model
class ParentAdminView(AdminModelView):
    form_overrides = {
        'role': SelectField
    }
    form_args = {
        'role': {
            'label': 'Role',
            'choices': [(role.name, role.value) for role in ParentRole],
            'coerce': lambda x: ParentRole[x] if isinstance(x, str) else x
        }
    }

# Custom view for the Puppy model
class PuppyAdminView(AdminModelView):
    form_overrides = {
        'status': SelectField
    }
    form_args = {
        'status': {
            'label': 'Status',
            'choices': [(status.name, status.value) for status in PuppyStatus],
            'coerce': lambda x: PuppyStatus[x] if isinstance(x, str) else x
        }
    }

# Add views for your models, using the new custom views
admin.add_view(ParentAdminView(Parent, db.session))
admin.add_view(PuppyAdminView(Puppy, db.session))
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