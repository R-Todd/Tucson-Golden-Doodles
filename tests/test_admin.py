import io
from unittest.mock import patch
from flask import url_for
from app.models import User, Parent, Puppy, HeroSection, AboutSection, ParentRole, SiteMeta, PuppyStatus

class TestAdminRoutes:
    """
    Test suite for admin authentication and model management.
    """

    def _login(self, client, username, password):
        """Helper function to log in a user."""
        return client.post(
            url_for('admin_auth.login'),
            data={'username': username, 'password': password},
            follow_redirects=True
        )

    def test_admin_login_logout(self, client, db):
        """
        GIVEN a User model for an admin.
        WHEN the admin logs in via the login form.
        THEN check for a successful response and that the "Logout" link is present.
        WHEN the admin clicks logout.
        THEN check that they are redirected and the login page is shown.

        This test validates the interaction between:
        - User model (app/models/user_models.py)
        - Login/Logout routes (app/routes/admin/routes.py)
        - Base template (app/templates/base.html)
        """
        # === ARRANGE ===
        # 1. Create the admin user.
        admin_user = User(username='admin')
        admin_user.set_password('password123')
        
        # 2. Add a SiteMeta object. The base template requires this for rendering
        #    the footer and other elements, which is necessary after a successful login redirect.
        db.session.add(SiteMeta(email='contact@test.com'))
        db.session.add(admin_user)
        db.session.commit()

        # === ACT & ASSERT (LOGIN) ===
        # 3. Log in the user and check the response.
        response = self._login(client, 'admin', 'password123')
        assert response.status_code == 200
        # Check for content unique to the admin dashboard.
        assert b'Tucson Golden Doodles Admin' in response.data
        # This confirms the fix in `base.html` was successful.
        assert b'Logout' in response.data

        # === ACT & ASSERT (LOGOUT) ===
        # 4. Request the logout URL and check the final page content.
        response = client.get(url_for('admin_auth.logout'), follow_redirects=True)
        assert response.status_code == 200
        # After logout, the user should be on a public page that shows the Admin Login link.
        assert b'Admin Login' in response.data
        assert b'Logout' not in response.data


    @patch('app.routes.admin.views.upload_image', return_value='http://fake-s3-url.com/puppy.jpg')
    def test_puppy_image_upload(self, mock_upload, client, db):
        """
        GIVEN a logged-in admin user and existing parent dogs.
        WHEN a new Puppy is created via the Flask-Admin form with valid data and an image.
        THEN check the response is successful, the image upload was handled, and the puppy exists in the database.
        
        This test validates the interaction between:
        - Puppy model (app/models/puppy_models.py)
        - PuppyAdminView (app/routes/admin/views.py)
        - Image Uploader Patch (app/utils/image_uploader.py)
        """
        # === ARRANGE ===
        # 1. Create and log in the admin user.
        admin_user = User(username='admin')
        admin_user.set_password('password123')
        
        # 2. Add the required SiteMeta object for template rendering.
        db.session.add(SiteMeta(email='test@test.com'))
        
        # 3. Create Parent objects, as their IDs are required by the Puppy form.
        mom = Parent(name='Test Mom', role=ParentRole.MOM)
        dad = Parent(name='Test Dad', role=ParentRole.DAD)
        db.session.add_all([admin_user, mom, dad])
        db.session.commit()
        self._login(client, 'admin', 'password123')

        # 4. Prepare the form data, ensuring it matches all required fields.
        fake_image = (io.BytesIO(b"this is a fake puppy image"), 'puppy.jpg')
        form_data = {
            'name': 'Test Puppy',
            'birth_date': '2024-01-01',
            'status': 'AVAILABLE',  # Use the Enum *name* as a string
            'mom': mom.id,          # Use the parent's actual ID
            'dad': dad.id,
            'image_upload': fake_image
        }

        # === ACT ===
        # 5. Make the POST request, capturing the response for analysis.
        response = client.post(
            url_for('puppy.create_view'),
            data=form_data,
            content_type='multipart/form-data', # Essential for file uploads
            follow_redirects=True
        )

        # === ASSERT ===
        # 6. Check for a successful response code.
        assert response.status_code == 200
        
        # 7. Check for Flask-Admin's default success message.
        assert b'Record was successfully created.' in response.data

        # 8. Confirm the mocked image upload function was called.
        mock_upload.assert_called_once()

        # 9. Query the database to ensure the puppy was actually created.
        puppy = Puppy.query.filter_by(name='Test Puppy').first()
        assert puppy is not None
        
        # 10. Verify the data was saved correctly.
        assert puppy.status == PuppyStatus.AVAILABLE
        assert puppy.main_image_url == 'http://fake-s3-url.com/puppy.jpg'

    # --- Other tests from your original file are preserved below ---

    def test_admin_auth_redirect(self, client, db):
        """
        GIVEN a Flask application
        WHEN the admin index is accessed without authentication
        THEN check that the user is redirected to the login page
        """
        db.session.add(SiteMeta(email='test@test.com'))
        db.session.commit()

        response = client.get(url_for('admin.index'), follow_redirects=True)
        assert response.status_code == 200
        assert b'Admin Login' in response.data

    @patch('app.routes.admin.views.upload_image', return_value='http://fake-s3-url.com/image.jpg')
    def test_parent_image_upload(self, mock_upload, client, db):
        """
        GIVEN an authenticated admin user
        WHEN a new Parent is created with an image upload
        THEN check that the 'upload_image' function was called and the URL was saved
        """
        admin_user = User(username='admin')
        admin_user.set_password('password123')
        db.session.add(admin_user)
        db.session.commit()
        self._login(client, 'admin', 'password123')

        fake_image = (io.BytesIO(b"this is a fake parent image"), 'parent.jpg')

        response = client.post(
            url_for('parent.create_view'),
            data={
                'name': 'Test Dad',
                'role': 'DAD',
                'breed': 'Test Breed',
                'image_upload': fake_image
            },
            content_type='multipart/form-data',
            follow_redirects=True
        )

        assert response.status_code == 200
        mock_upload.assert_called_once()
        parent = Parent.query.filter_by(name='Test Dad').first()
        assert parent is not None
        assert parent.main_image_url == 'http://fake-s3-url.com/image.jpg'


    @patch('app.routes.admin.views.upload_image', return_value='http://fake-s3-url.com/hero.jpg')
    def test_hero_section_image_upload(self, mock_upload, client, db):
        """
        GIVEN an authenticated admin user
        WHEN the Hero Section is edited with a new image
        THEN check that the image URL is updated
        """
        hero = HeroSection(title='Old Title')
        admin_user = User(username='admin')
        admin_user.set_password('password123')
        db.session.add_all([hero, admin_user])
        db.session.commit()
        self._login(client, 'admin', 'password123')

        fake_image = (io.BytesIO(b"this is a fake hero image"), 'hero.jpg')

        client.post(
            url_for('herosection.edit_view', id=hero.id),
            data={
                'title': 'New Title',
                'image_upload': fake_image
            },
            content_type='multipart/form-data',
            follow_redirects=True
        )

        mock_upload.assert_called_once()
        db.session.refresh(hero)
        assert hero.image_url == 'http://fake-s3-url.com/hero.jpg'
        assert hero.title == 'New Title'