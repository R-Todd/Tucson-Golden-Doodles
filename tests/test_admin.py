import io
from unittest.mock import patch
from flask import url_for
from app.models import (
    User, Parent, Puppy, SiteMeta, ParentRole, PuppyStatus, Review
)
from bs4 import BeautifulSoup
from app.utils.image_uploader import upload_image

class TestAdminFunctionality:
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
        admin_user = User(username='admin')
        admin_user.set_password('password123')
        db.session.add(SiteMeta(email='contact@test.com'))
        db.session.add(admin_user)
        db.session.commit()

        login_response = self._login(client, 'admin', 'password123')
        assert login_response.status_code == 200
        assert b'Tucson Golden Doodles Admin' in login_response.data
        assert b'Logout' in login_response.data

        logout_response = client.get(url_for('admin_auth.logout'), follow_redirects=True)
        assert logout_response.status_code == 200
        assert b'Admin Login' in logout_response.data
        assert b'Logout' not in logout_response.data

    def test_unauthenticated_access_is_redirected(self, client, db):
        """
        GIVEN a non-authenticated user
        WHEN they attempt to access any admin model view (e.g., the Puppy list)
        THEN they should be redirected to the login page
        """
        db.session.add(SiteMeta(email='contact@test.com'))
        db.session.commit()
        response = client.get(url_for('puppy.index_view'), follow_redirects=True)
        assert response.status_code == 200
        assert b'Admin Login' in response.data
        assert b'Puppy' not in response.data

    # --- Puppy CRUD and Validation Tests ---

    def test_create_puppy_form_has_filtered_parents(self, client, db):
        """
        GIVEN a logged-in admin and multiple parents with 'MOM' and 'DAD' roles
        WHEN the 'Add Puppy' form page is requested
        THEN check that the 'Mother' dropdown only contains moms and the 'Father' dropdown only contains dads
        """
        admin_user = User(username='admin'); admin_user.set_password('pw')
        mom1 = Parent(name='Luna', role=ParentRole.MOM)
        mom2 = Parent(name='Bella', role=ParentRole.MOM)
        dad1 = Parent(name='Archie', role=ParentRole.DAD)
        dad2 = Parent(name='Rocky', role=ParentRole.DAD)
        db.session.add_all([admin_user, mom1, mom2, dad1, dad2, SiteMeta(email='c@t.com')])
        db.session.commit()
        self._login(client, 'admin', 'pw')

        response = client.get(url_for('puppy.create_view'))
        html = response.data.decode('utf-8')
        assert response.status_code == 200
        
        soup = BeautifulSoup(html, 'html.parser')
        mom_select = soup.find('select', {'name': 'mom'})
        assert mom_select is not None, "Mother dropdown not found"
        mom_options_text = [option.text for option in mom_select.find_all('option')]
        mom_options_values = [option.get('value') for option in mom_select.find_all('option')]

        assert mom1.name in mom_options_text
        assert mom2.name in mom_options_text
        assert str(mom1.id) in mom_options_values
        assert str(mom2.id) in mom_options_values
        assert dad1.name not in mom_options_text
        assert dad2.name not in mom_options_text
        assert str(dad1.id) not in mom_options_values
        assert str(dad2.id) not in mom_options_values

        dad_select = soup.find('select', {'name': 'dad'})
        assert dad_select is not None, "Father dropdown not found"
        dad_options_text = [option.text for option in dad_select.find_all('option')]
        dad_options_values = [option.get('value') for option in dad_select.find_all('option')]

        assert dad1.name in dad_options_text
        assert dad2.name in dad_options_text
        assert str(dad1.id) in dad_options_values
        assert str(dad2.id) in dad_options_values
        assert mom1.name not in dad_options_text
        assert mom2.name not in dad_options_text
        assert str(mom1.id) not in dad_options_values
        assert str(mom2.id) not in dad_options_values

    @patch('app.routes.admin.views.puppy_views.upload_image', return_value='http://fake-s3-url.com/new_puppy.jpg')
    def test_create_puppy_with_valid_data(self, mock_upload, client, db):
        """
        GIVEN a logged-in admin and existing parent records
        WHEN a new Puppy is created via POST with valid data and an image
        THEN check that a new Puppy record is created in the database with the correct image URL
        """
        admin_user = User(username='admin'); admin_user.set_password('pw')
        mom = Parent(name='Test Mom', role=ParentRole.MOM)
        dad = Parent(name='Test Dad', role=ParentRole.DAD)
        db.session.add_all([admin_user, mom, dad, SiteMeta(email='c@t.com')])
        db.session.commit()
        self._login(client, 'admin', 'pw')
        fake_image = (io.BytesIO(b"a fake image"), 'puppy.jpg')

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
        admin_user = User(username='admin'); admin_user.set_password('pw')
        mom = Parent(name='Test Mom', role=ParentRole.MOM)
        dad = Parent(name='Test Dad', role=ParentRole.DAD)
        db.session.add_all([admin_user, mom, dad, SiteMeta(email='c@t.com')])
        db.session.commit()
        self._login(client, 'admin', 'pw')

        response = client.post(
            url_for('puppy.create_view'),
            data={
                'name': '',
                'birth_date': '2025-07-21',
                'status': 'AVAILABLE',
                'mom': mom.id,
                'dad': dad.id,
            },
            follow_redirects=True
        )

        assert response.status_code == 200
        assert b'This field is required.' in response.data
        assert Puppy.query.count() == 0

    # --- Parent CRUD and Validation Tests ---

    @patch('app.utils.image_uploader.upload_image')
    def test_edit_parent_record(self, mock_upload, client, db):
        """
        GIVEN a logged-in admin and an existing Parent record
        WHEN the admin edits the parent's name AND uploads an alternate image
        THEN check that the name and the alternate image URL are saved to the database
        """
        admin_user = User(username='admin'); admin_user.set_password('pw')
        parent = Parent(name='Old Name', role=ParentRole.DAD)
        db.session.add_all([admin_user, parent, SiteMeta(email='c@t.com')])
        db.session.commit()
        self._login(client, 'admin', 'pw')

        # Fix: Mock the S3 upload to return a URL that matches the expected S3 format
        mock_upload.return_value = 'https://tucson-golden-doodles-images.s3.us-east-1.amazonaws.com/parents_alternates/mock_uuid-alternate1.jpg'
        fake_alternate_image = (io.BytesIO(b"a fake alternate image"), 'alternate1.jpg')

        response = client.post(
            url_for('parent.edit_view', id=parent.id),
            data={
                'name': 'New Name',
                'role': 'DAD',
                'alternate_image_upload_1': fake_alternate_image
            },
            content_type='multipart/form-data',
            follow_redirects=True
        )

        assert response.status_code == 200
        db.session.refresh(parent)
        assert parent.name == 'New Name'
        assert parent.alternate_image_url_1 == 'https://tucson-golden-doodles-images.s3.us-east-1.amazonaws.com/parents_alternates/mock_uuid-alternate1.jpg'
        
        mock_upload.assert_called_once_with(fake_alternate_image[0], folder='parents_alternates')

    def test_delete_review_record(self, client, db):
        """
        GIVEN a logged-in admin and an existing Review record
        WHEN the admin deletes the record via POST to the delete view
        THEN check that the record is removed from the database
        """
        admin_user = User(username='admin'); admin_user.set_password('pw')
        review_to_delete = Review(author_name='ToBeDeleted', testimonial_text='...')
        db.session.add_all([admin_user, review_to_delete, SiteMeta(email='c@t.com')])
        db.session.commit()
        self._login(client, 'admin', 'pw')
        review_id = review_to_delete.id

        response = client.post(
            url_for('review.delete_view', id=review_id),
            follow_redirects=True
        )

        assert response.status_code == 200
        assert b'Record was successfully deleted.' in response.data
        deleted_review = db.session.get(Review, review_id)
        assert deleted_review is None