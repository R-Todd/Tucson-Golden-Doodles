import io
from unittest.mock import patch
from flask import url_for
from datetime import date
from app.models import (
    User, Parent, Puppy, SiteMeta, ParentRole, PuppyStatus, Review
)

class TestAdminRoutes:
    """
    A comprehensive test suite for the Flask-Admin portal, covering
    authentication, authorization, and CRUD operations.
    """

    def _login(self, client, username, password):
        """
        Helper function to log in a user.
        It returns the response without following redirects.
        """
        return client.post(
            url_for('admin_auth.login'),
            data={'username': username, 'password': password},
            follow_redirects=False
        )

    # --- Authentication and Authorization Tests ---

    def test_admin_login_logout(self, client, db):
        """
        GIVEN a User model for an admin.
        WHEN the admin logs in and then logs out.
        THEN check for successful login and subsequent successful logout.
        """
        # ARRANGE
        admin_user = User(username='admin')
        admin_user.set_password('password123')
        db.session.add(SiteMeta(email='contact@test.com'))
        db.session.add(admin_user)
        db.session.commit()

        # ACT & ASSERT (LOGIN)
        login_response = self._login(client, 'admin', 'password123')
        assert login_response.status_code == 302

        dashboard_response = client.get(url_for('admin.index'))
        assert dashboard_response.status_code == 200
        assert b'Logout' in dashboard_response.data

        # ACT & ASSERT (LOGOUT)
        logout_response = client.get(url_for('admin_auth.logout'), follow_redirects=True)
        assert logout_response.status_code == 200
        assert b'Admin Login' in logout_response.data
        assert b'Logout' not in logout_response.data

    def test_admin_login_with_invalid_credentials(self, client, db):
        """
        GIVEN an existing admin user.
        WHEN an attempt is made to log in with the wrong password.
        THEN the response should contain an error message.
        """
        # ARRANGE
        admin_user = User(username='admin')
        admin_user.set_password('correct_password')
        db.session.add(admin_user)
        db.session.commit()

        # ACT
        response = client.post(
            url_for('admin_auth.login'),
            data={'username': 'admin', 'password': 'wrong_password'},
            follow_redirects=True
        )

        # ASSERT
        assert response.status_code == 200
        assert b'Invalid username or password' in response.data

    def test_unauthenticated_access_to_model_view(self, client, db):
        """
        GIVEN a non-authenticated user.
        WHEN they try to access an admin model view.
        THEN they should be redirected to the login page.
        """
        # ARRANGE
        db.session.add(SiteMeta(email='contact@test.com'))
        db.session.commit()

        # ACT
        response = client.get(url_for('puppy.index_view'), follow_redirects=True)

        # ASSERT
        assert response.status_code == 200
        assert b'Admin Login' in response.data
        assert b'Puppy' not in response.data

    def test_admin_auth_redirect(self, client, db):
        """
        GIVEN a non-authenticated user.
        WHEN the admin index is accessed.
        THEN the user is redirected to the login page.
        """
        # ARRANGE
        db.session.add(SiteMeta(email='test@test.com'))
        db.session.commit()

        # ACT
        response = client.get(url_for('admin.index'), follow_redirects=True)
        
        # ASSERT
        assert response.status_code == 200
        assert b'Admin Login' in response.data

    # --- CRUD and Data Validation Tests ---

    @patch('app.routes.admin.views.upload_image', return_value='http://fake-s3-url.com/puppy.jpg')
    def test_create_puppy_with_image(self, mock_upload, client, db):
        """
        GIVEN a logged-in admin.
        WHEN a new Puppy is created with valid data and an image.
        THEN check the puppy exists and the flash message is shown.
        """
        # ARRANGE
        admin_user = User(username='admin')
        admin_user.set_password('password123')
        mom = Parent(name='Test Mom', role=ParentRole.MOM)
        dad = Parent(name='Test Dad', role=ParentRole.DAD)
        db.session.add_all([admin_user, mom, dad, SiteMeta(email='contact@test.com')])
        db.session.commit()
        
        # Log in first
        self._login(client, 'admin', 'password123')
        
        fake_image = (io.BytesIO(b"this is a fake puppy image"), 'puppy.jpg')

        # ACT (Step 1: POST the data, but don't follow the redirect)
        create_response = client.post(
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
            follow_redirects=False # Important!
        )
        
        # ASSERT (Step 1: Check that a redirect occurred)
        assert create_response.status_code == 302

        # ACT (Step 2: Follow the redirect manually to the puppy list page)
        list_view_response = client.get(url_for('puppy.index_view'))
        
        # ASSERT (Step 2: Check for the flash message on the list page)
        assert list_view_response.status_code == 200
        assert b'Record was successfully created.' in list_view_response.data
        
        # Final assertions
        mock_upload.assert_called_once()
        puppy = Puppy.query.filter_by(name='Test Puppy').first()
        assert puppy is not None
        assert puppy.main_image_url == 'http://fake-s3-url.com/puppy.jpg'

    def test_create_parent_with_missing_role_fails(self, client, db):
        """
        GIVEN a logged-in admin.
        WHEN they try to create a Parent without a required 'role'.
        THEN the creation should fail and show an error.
        """
        # ARRANGE
        admin_user = User(username='admin')
        admin_user.set_password('password123')
        db.session.add(admin_user)
        db.session.commit()
        self._login(client, 'admin', 'password123')

        # ACT
        response = client.post(
            url_for('parent.create_view'),
            data={'name': 'Incomplete Parent'},
            follow_redirects=True
        )

        # ASSERT
        assert response.status_code == 200
        assert b'This field is required.' in response.data
        parent = Parent.query.filter_by(name='Incomplete Parent').first()
        assert parent is None

    def test_edit_existing_review(self, client, db):
        """
        GIVEN a logged-in admin and an existing review.
        WHEN the admin edits the review's text.
        THEN the change should be saved to the database.
        """
        # ARRANGE
        admin_user = User(username='admin')
        admin_user.set_password('password123')
        review = Review(author_name='Old Author', testimonial_text='Old Text')
        db.session.add_all([admin_user, review])
        db.session.commit()
        self._login(client, 'admin', 'password123')

        # ACT
        client.post(
            url_for('review.edit_view', id=review.id),
            data={
                'author_name': 'New Author',
                'testimonial_text': 'This is the updated text.'
            },
            follow_redirects=True
        )

        # ASSERT
        db.session.refresh(review)
        assert review.author_name == 'New Author'
        assert review.testimonial_text == 'This is the updated text.'

    def test_delete_existing_record(self, client, db):
        """
        GIVEN a logged-in admin and an existing record.
        WHEN the admin deletes the record.
        THEN it should be removed from the database.
        """
        # ARRANGE
        admin_user = User(username='admin')
        admin_user.set_password('password123')
        review_to_delete = Review(author_name='To Be Deleted', testimonial_text='Delete me')
        db.session.add_all([admin_user, review_to_delete])
        db.session.commit()
        self._login(client, 'admin', 'password123')

        # ACT
        response = client.post(
            url_for('review.delete_view', id=review_to_delete.id),
            follow_redirects=True
        )

        # ASSERT
        assert response.status_code == 200
        assert b'Record was successfully deleted.' in response.data
        deleted_review = Review.query.get(review_to_delete.id)
        assert deleted_review is None