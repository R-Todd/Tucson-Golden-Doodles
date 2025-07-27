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
    # (These tests are unchanged)
    def test_admin_login_and_logout(self, client, db):
        admin_user = User(username='admin')
        admin_user.set_password('password123')
        db.session.add(SiteMeta(email='contact@test.com'))
        db.session.add(admin_user)
        db.session.commit()
        login_response = self._login(client, 'admin', 'password123')
        assert login_response.status_code == 200
        assert b'Tucson Golden Doodles Admin' in login_response.data
        logout_response = client.get(url_for('admin_auth.logout'), follow_redirects=True)
        assert logout_response.status_code == 200
        assert b'Admin Login' in logout_response.data

    def test_unauthenticated_access_is_redirected(self, client, db):
        db.session.add(SiteMeta(email='contact@test.com'))
        db.session.commit()
        response = client.get(url_for('puppy.index_view'), follow_redirects=True)
        assert response.status_code == 200
        assert b'Admin Login' in response.data

    # --- Puppy CRUD and Validation Tests ---

    def test_create_puppy_form_has_filtered_parents(self, client, db):
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
        
        # --- REVERTED: Use 'mom' as the field name ---
        mom_select = soup.find('select', {'name': 'mom'})
        assert mom_select is not None, "Mother dropdown not found"
        mom_options_text = [option.text for option in mom_select.find_all('option')]
        assert 'Luna' in mom_options_text and 'Bella' in mom_options_text
        assert 'Archie' not in mom_options_text

        # --- REVERTED: Use 'dad' as the field name ---
        dad_select = soup.find('select', {'name': 'dad'})
        assert dad_select is not None, "Father dropdown not found"
        dad_options_text = [option.text for option in dad_select.find_all('option')]
        assert 'Archie' in dad_options_text and 'Rocky' in dad_options_text
        assert 'Luna' not in dad_options_text

    @patch('app.routes.admin.views.puppy_views.upload_image', return_value='http://fake-s3-url.com/new_puppy.jpg')
    def test_create_puppy_with_valid_data(self, mock_upload, client, db):
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
                # --- REVERTED: Use 'mom' and 'dad' as form field keys ---
                'mom': mom.id,
                'dad': dad.id,
                'image_upload': fake_image
            },
            content_type='multipart/form-data',
            follow_redirects=True
        )
        assert response.status_code == 200
        assert b'Record was successfully created.' in response.data
        puppy = Puppy.query.filter_by(name='Test Puppy').first()
        assert puppy is not None
        assert puppy.mom == mom

    def test_create_puppy_with_missing_name_fails(self, client, db):
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
                # --- REVERTED: Use 'mom' and 'dad' as form field keys ---
                'mom': mom.id,
                'dad': dad.id,
            },
            follow_redirects=True
        )
        assert response.status_code == 200
        assert b'This field is required.' in response.data

    # --- Parent CRUD and Validation Tests ---
    # (These tests are unchanged)
    @patch('app.routes.admin.views.parent_views.upload_image')
    def test_edit_parent_record(self, mock_upload, client, db):
        admin_user = User(username='admin'); admin_user.set_password('pw')
        parent = Parent(name='Old Name', role=ParentRole.DAD)
        db.session.add_all([admin_user, parent, SiteMeta(email='c@t.com')])
        db.session.commit()
        self._login(client, 'admin', 'pw')
        mock_upload.return_value = 'https://example.com/image.jpg'
        fake_image = (io.BytesIO(b"fake image data"), 'alternate1.jpg')
        response = client.post(
            url_for('parent.edit_view', id=parent.id),
            data={'name': 'New Name', 'role': 'DAD', 'alternate_image_upload_1': fake_image},
            content_type='multipart/form-data',
            follow_redirects=True
        )
        assert response.status_code == 200
        db.session.refresh(parent)
        assert parent.name == 'New Name'
        assert parent.alternate_image_url_1 == 'https://example.com/image.jpg'

    def test_delete_review_record(self, client, db):
        admin_user = User(username='admin'); admin_user.set_password('pw')
        review = Review(author_name='ToBeDeleted', testimonial_text='...')
        db.session.add_all([admin_user, review, SiteMeta(email='c@t.com')])
        db.session.commit()
        self._login(client, 'admin', 'pw')
        review_id = review.id
        response = client.post(url_for('review.delete_view', id=review_id), follow_redirects=True)
        assert response.status_code == 200
        assert b'Record was successfully deleted.' in response.data
        assert db.session.get(Review, review_id) is None