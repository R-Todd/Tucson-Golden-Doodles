import io
from unittest.mock import patch
from flask import url_for
from app.models import User, Parent, Puppy, HeroSection, AboutSection, ParentRole, SiteMeta

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
        GIVEN a user model
        WHEN a new user is created
        THEN check that they can log in and log out
        """
        admin_user = User(username='admin')
        admin_user.set_password('password123')
        # FIX: Add SiteMeta object needed for rendering the redirected admin page.
        db.session.add(SiteMeta(email='test@test.com'))
        db.session.add(admin_user)
        db.session.commit()

        response = self._login(client, 'admin', 'password123')
        assert response.status_code == 200
        assert b'Tucson Golden Doodles Admin' in response.data
        assert b'Logout' in response.data

        response = client.get(url_for('admin_auth.logout'), follow_redirects=True)
        assert response.status_code == 200
        assert b'Admin Login' in response.data

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

    @patch('app.routes.admin.views.upload_image', return_value='http://fake-s3-url.com/puppy.jpg')
    def test_puppy_image_upload(self, mock_upload, client, db):
        """
        GIVEN an authenticated admin user
        WHEN a new Puppy is created with an image upload
        THEN check that the image URL is correctly saved
        """
        admin_user = User(username='admin')
        admin_user.set_password('password123')
        mom = Parent(name='Test Mom', role=ParentRole.MOM)
        dad = Parent(name='Test Dad', role=ParentRole.DAD)
        # FIX: Add SiteMeta object needed for rendering the admin page.
        db.session.add(SiteMeta(email='test@test.com'))
        db.session.add_all([admin_user, mom, dad])
        db.session.commit()
        self._login(client, 'admin', 'password123')

        fake_image = (io.BytesIO(b"this is a fake puppy image"), 'puppy.jpg')

        client.post(
            url_for('puppy.create_view'),
            data={
                'name': 'Test Puppy',
                'birth_date': '2024-01-01',
                'status': 'AVAILABLE',
                'mom': mom.id,
                'dad': dad.id,
                'image_upload': fake_image
            },
            content_type='multipart/form-data',
            follow_redirects=True
        )

        mock_upload.assert_called_once()
        puppy = Puppy.query.filter_by(name='Test Puppy').first()
        assert puppy is not None
        assert puppy.main_image_url == 'http://fake-s3-url.com/puppy.jpg'

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
