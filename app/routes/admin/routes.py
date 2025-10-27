# app/routes/admin/routes.py

# Added imports for the new route and form
from flask import redirect, url_for, request, render_template, flash
from flask_login import current_user, login_user, logout_user, login_required # Added login_required
from flask_admin.menu import MenuLink
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField
from wtforms.fields import FileField
from wtforms.validators import Optional
from app.utils.image_uploader import upload_image # Added uploader import

from app import db
from app.models import (
    User, Parent, Puppy, Review, HeroSection, AboutSection, GalleryImage, AnnouncementBanner,
    ParentsPageHeader # Model import kept
)
from . import bp, admin
# Removed the import for ParentsPageHeaderAdminView
from .views import (
    ParentAdminView, PuppyAdminView, HeroSectionAdminView,
    AboutSectionAdminView, AnnouncementBannerAdminView, ReviewAdminView, AdminModelView, GalleryImageAdminView
)


# Register admin views for different models (No change here)
admin.add_view(ParentAdminView(Parent, db.session))
admin.add_view(PuppyAdminView(Puppy, db.session))

# Register admin views for site content using Bootstrap 5 templates (No change here)
admin.add_view(ReviewAdminView(Review, db.session))
admin.add_view(HeroSectionAdminView(HeroSection, db.session, name="Hero Section"))
admin.add_view(AboutSectionAdminView(AboutSection, db.session, name="About Section"))
admin.add_view(AnnouncementBannerAdminView(AnnouncementBanner, db.session, name="Announcement Banner"))
admin.add_view(GalleryImageAdminView(GalleryImage, db.session, name="Gallery Images"))

# Removed the registration for ParentsPageHeaderAdminView


# Add a logout link to the admin menu (No change here)
admin.add_link(MenuLink(name='Logout', category='', url='/admin/logout'))

# --- Form for the Parents Page Header ---
# Defined directly in this file now
class ParentsHeaderForm(FlaskForm):
    title = StringField('Title')
    tagline = StringField('Tagline')
    description_points = TextAreaField(
        'Description Points',
        render_kw={
            'rows': 10,
            'style': 'font-family: monospace;',
            'placeholder': 'Enter each point on a new line, like:\nTitle|Description\nAnother Title|Another description...'
        }
    )
    image_upload = FileField('Upload Header Image (Optional)')


# --- NEW ROUTE for Editing Parents Page Header ---
@bp.route('/parents/edit-header', methods=['GET', 'POST'])
@login_required # Protects this route
def edit_parents_header():
    # Fetch or create the single header record
    header_content = ParentsPageHeader.query.first()
    if not header_content:
        header_content = ParentsPageHeader()
        db.session.add(header_content)
        # db.session.commit() # Optional: commit defaults immediately

    form = ParentsHeaderForm(obj=header_content) # Pre-populate form with existing data

    if form.validate_on_submit(): # If form submitted and valid
        # Update model from form data
        header_content.title = form.title.data
        header_content.tagline = form.tagline.data
        header_content.description_points = form.description_points.data

        # Handle file upload
        file = request.files.get('image_upload')
        if file and file.filename:
            s3_key = upload_image(file, folder='parents_header') # Upload to S3
            if s3_key:
                header_content.image_s3_key = s3_key # Save the S3 key

        db.session.commit() # Save changes to database
        flash('Parents page header updated successfully!', 'success')
        # Redirect back to the main Parents admin list page
        return redirect(url_for('parent.index_view'))

    # If GET request or form validation failed, render the edit template
    # Path is updated to reflect correct location
    return render_template('admin/parent/parents_header_edit.html', form=form, model=header_content)
# --- END OF NEW ROUTE ---


# --- Login/Logout Routes ---
# (These remain unchanged from previous versions)
@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('admin.index'))

    if request.method == 'POST':
        user = User.query.filter_by(username=request.form['username']).first()

        if user is None or not user.check_password(request.form['password']):
            flash('Invalid username or password', 'danger')
        else:
            login_user(user)
            return redirect(url_for('admin.index'))

    return render_template('login.html')

@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.index'))