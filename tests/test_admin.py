import io
from unittest.mock import patch
from flask import url_for
from app.models import (
    User, Parent, Puppy, SiteMeta, ParentRole, PuppyStatus, Review
)

# By grouping tests into a class, we can share helper methods like _login
# and keep the test suite organized.

class TestAdminFunctionality:
    """
    A comprehensive test suite for the Flask-Admin portal, covering
    authentication, authorization, and model-specific CRUD operations.
    """

    def _login(self, client, username, password):
        """Helper function to log in a user."""
        return client.post(
            url_for('admin_auth.login'),
            data={'username': username, 'password': password},
            follow_redirects=True
        )

    # --- Authentication and Authorization Tests ---

    def test_admin_login_and_logout(self, client, db):
        """
        GIVEN a User model for an admin
        WHEN the admin logs in via a POST to '/admin/login'
        THEN check that the response is successful and they can access the dashboard
        WHEN the admin logs out via a GET to '/admin/logout'
        THEN check that they are redirected to the homepage and can no longer see admin links
        """
        # ARRANGE: Create a test admin user and site metadata
        admin_user = User(username='admin')
        admin_user.set_password('password123')
        db.session.add(SiteMeta(email='contact@test.com'))
        db.session.add(admin_user)
        db.session.commit()

        # ACT & ASSERT (LOGIN)
        login_response = self._login(client, 'admin', 'password123')
        assert login_response.status_code == 200
        assert b'Tucson Golden Doodles Admin' in login_response.data # Check for dashboard content
        assert b'Logout' in login_response.data

        # ACT & ASSERT (LOGOUT)
        logout_response = client.get(url_for('admin_auth.logout'), follow_redirects=True)
        assert logout_response.status_code == 200
        # After logout, they should be on the public site, which shows "Admin Login"
        assert b'Admin Login' in logout_response.data
        assert b'Logout' not in logout_response.data

    def test_unauthenticated_access_is_redirected(self, client, db):
        """
        GIVEN a non-authenticated user
        WHEN they attempt to access any admin model view (e.g., the Puppy list)
        THEN they should be redirected to the login page
        """
        # ARRANGE
        db.session.add(SiteMeta(email='contact@test.com'))
        db.session.commit()

        # ACT
        response = client.get(url_for('puppy.index_view'), follow_redirects=True)

        # ASSERT
        assert response.status_code == 200
        # The content of the login page should be present
        assert b'Admin Login' in response.data
        # The content of the protected page should NOT be present
        assert b'Puppy' not in response.data

    # --- Puppy CRUD and Validation Tests ---

    def test_create_puppy_form_has_filtered_parents(self, client, db):
        """
        GIVEN a logged-in admin and multiple parents with 'MOM' and 'DAD' roles
        WHEN the 'Add Puppy' form page is requested
        THEN check that the 'Mother' dropdown only contains moms and the 'Father' dropdown only contains dads
        """
        # ARRANGE
        admin_user = User(username='admin'); admin_user.set_password('pw')
        mom1 = Parent(name='Luna', role=ParentRole.MOM)
        mom2 = Parent(name='Bella', role=ParentRole.MOM)
        dad1 = Parent(name='Archie', role=ParentRole.DAD)
        dad2 = Parent(name='Rocky', role=ParentRole.DAD)
        db.session.add_all([admin_user, mom1, mom2, dad1, dad2, SiteMeta(email='c@t.com')])
        db.session.commit()
        self._login(client, 'admin', 'pw')

        # ACT
        response = client.get(url_for('puppy.create_view'))
        html = response.data.decode('utf-8')

        # ASSERT
        assert response.status_code == 200
        # Check that mom names are present and dad names are not in the mom dropdown
        assert 'value="' + str(mom1.id) + '">Luna' in html
        assert 'value="' + str(mom2.id) + '">Bella' in html
        assert 'value="' + str(dad1.id) + '">Archie' not in html
        assert 'value="' + str(dad2.id) + '">Rocky' not in html

    @patch('app.routes.admin.views.puppy_views.upload_image', return_value='http://fake-s3-url.com/new_puppy.jpg')
    def test_create_puppy_with_valid_data(self, mock_upload, client, db):
        """
        GIVEN a logged-in admin and existing parent records
        WHEN a new Puppy is created via POST with valid data and an image
        THEN check that a new Puppy record is created in the database with the correct image URL
        """
        # ARRANGE
        admin_user = User(username='admin'); admin_user.set_password('pw')
        mom = Parent(name='Test Mom', role=ParentRole.MOM)
        dad = Parent(name='Test Dad', role=ParentRole.DAD)
        db.session.add_all([admin_user, mom, dad, SiteMeta(email='c@t.com')])
        db.session.commit()
        self._login(client, 'admin', 'pw')
        fake_image = (io.BytesIO(b"a fake image"), 'puppy.jpg')

        # ACT
        response = client.post(
            url_for('puppy.create_view'),
            data={
                'name': 'Test Puppy',
                'birth_date': '2025-07-21',
                'status': 'AVAILABLE',
                'mom': mom.id,
                'dad': dad.id,
                'image_upload': fake_image
            },
            content_type='multipart/form-data',
            follow_redirects=True
        )

        # ASSERT
        assert response.status_code == 200
        assert b'Record was successfully created.' in response.data
        mock_upload.assert_called_once()
        puppy = Puppy.query.filter_by(name='Test Puppy').first()
        assert puppy is not None
        assert puppy.mom == mom
        assert puppy.main_image_url == 'http://fake-s3-url.com/new_puppy.jpg'

    def test_create_puppy_with_missing_name_fails(self, client, db):
        """
        GIVEN a logged-in admin
        WHEN a new Puppy is created via POST with a required field missing (e.g., name)
        THEN check that the form is re-rendered with a validation error message
        """
        # ARRANGE
        admin_user = User(username='admin'); admin_user.set_password('pw')
        mom = Parent(name='Test Mom', role=ParentRole.MOM)
        dad = Parent(name='Test Dad', role=ParentRole.DAD)
        db.session.add_all([admin_user, mom, dad, SiteMeta(email='c@t.com')])
        db.session.commit()
        self._login(client, 'admin', 'pw')

        # ACT
        response = client.post(
            url_for('puppy.create_view'),
            data={
                'name': '', # Missing name
                'birth_date': '2025-07-21',
                'status': 'AVAILABLE',
                'mom': mom.id,
                'dad': dad.id,
            },
            follow_redirects=True
        )

        # ASSERT
        assert response.status_code == 200
        assert b'This field is required.' in response.data
        assert Puppy.query.count() == 0 # Ensure no puppy was created

    # --- Parent CRUD and Validation Tests ---

    def test_edit_parent_record(self, client, db):
        """
        GIVEN a logged-in admin and an existing Parent record
        WHEN the admin edits the parent's name via POST to the edit view
        THEN check that the change is saved to the database
        """
        # ARRANGE
        admin_user = User(username='admin'); admin_user.set_password('pw')
        parent = Parent(name='Old Name', role=ParentRole.DAD)
        db.session.add_all([admin_user, parent, SiteMeta(email='c@t.com')])
        db.session.commit()
        self._login(client, 'admin', 'pw')

        # ACT
        client.post(
            url_for('parent.edit_view', id=parent.id),
            data={'name': 'New Name', 'role': 'DAD'},
            follow_redirects=True
        )

        # ASSERT
        db.session.refresh(parent)
        assert parent.name == 'New Name'

    def test_delete_review_record(self, client, db):
        """
        GIVEN a logged-in admin and an existing Review record
        WHEN the admin deletes the record via POST to the delete view
        THEN check that the record is removed from the database
        """
        # ARRANGE
        admin_user = User(username='admin'); admin_user.set_password('pw')
        review_to_delete = Review(author_name='ToBeDeleted', testimonial_text='...')
        db.session.add_all([admin_user, review_to_delete, SiteMeta(email='c@t.com')])
        db.session.commit()
        self._login(client, 'admin', 'pw')
        review_id = review_to_delete.id

        # ACT
        response = client.post(
            url_for('review.delete_view', id=review_id),
            follow_redirects=True
        )

        # ASSERT
        assert response.status_code == 200
        assert b'Record was successfully deleted.' in response.data
        deleted_review = db.session.get(Review, review_id)
        assert deleted_review is None