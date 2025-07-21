# app/routes/admin/views/base.py

from flask import request, url_for, redirect
from flask_admin import AdminIndexView, expose
from flask_admin.contrib.sqla import ModelView
from flask_login import current_user

class MyAdminIndexView(AdminIndexView):
    """ Custom admin index view that requires authentication. """
    @expose('/')
    def index(self):
        if not current_user.is_authenticated:
            return redirect(url_for('admin_auth.login'))
        return super(MyAdminIndexView, self).index()

class AdminModelView(ModelView):
    """ Base ModelView that enforces authentication for all model pages. """
    def is_accessible(self):
        return current_user.is_authenticated

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('admin_auth.login', next=request.url))