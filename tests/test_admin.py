# tests/test_admin.py

import io
from unittest.mock import patch, MagicMock
from flask import url_for
from app.models import (
    User, Parent, Puppy, SiteDetails, ParentRole, PuppyStatus, Review
)
from bs4 import BeautifulSoup

class TestAdminFunctionality:
    def _login(self, client, username, password):
        """Helper function to log in a user."""
        return client.post(
            url_for('admin_auth.login'),
            data={'username': username, 'password': password},
            follow_redirects=True
        )

    # --- Authentication tests remain the same ---
    def test_admin_login_and_logout(self, client, db):
        admin_user = User(username='admin'); admin_user.set_password('password123')
        db.session.add(SiteDetails(email='contact@test.com'))
        db.session.add(admin_user)
        db.session.commit()
        login_response = self._login(client, 'admin', 'password123')
        assert login_response.status_code == 200
        assert b'Tucson Golden Doodles' in login_response.data
        logout_response = client.get(url_for('admin_auth.logout'), follow_redirects=True)
        assert logout_response.status_code == 200
        assert b'Admin Login' in logout_response.data

    # --- Puppy CRUD Tests (MODIFIED) ---

    # This patch is correct as upload_image is used in the view.
    @patch('app.routes.admin.views.puppy_views.upload_image', return_value='puppies/new_puppy.jpg')
    def test_create_puppy_with_valid_data_saves_s3_key(self, mock_upload, client, db):
        admin_user = User(username='admin'); admin_user.set_password('pw')
        mom = Parent(name='Test Mom', role=ParentRole.MOM)
        dad = Parent(name='Test Dad', role=ParentRole.DAD)
        db.session.add_all([admin_user, mom, dad, SiteDetails(email='c@t.com')])
        db.session.commit()
        self._login(client, 'admin', 'pw')
        fake_image = (io.BytesIO(b"a fake image"), 'puppy.jpg')
        
        response = client.post(
            url_for('puppy.create_view'),
            data={
                'name': 'Test Puppy',
                'birth_date': '2025-07-21',
                'status': 'AVAILABLE',
                'mom_id': mom.id,
                'dad_id': dad.id,
                'image_upload': fake_image
            },
            content_type='multipart/form-data',
            follow_redirects=True
        )
        assert response.status_code == 200
        assert b'Record was successfully created.' in response.data
        
        puppy = Puppy.query.filter_by(name='Test Puppy').first()
        assert puppy is not None
        assert puppy.main_image_s3_key == 'puppies/new_puppy.jpg'
        mock_upload.assert_called_once()

    # --- Parent CRUD Tests (MODIFIED) ---

    @patch('app.routes.admin.views.parent_views.upload_image')
    def test_edit_parent_record_saves_s3_keys(self, mock_upload, client, db):
        admin_user = User(username='admin'); admin_user.set_password('pw')
        parent = Parent(name='Old Name', role=ParentRole.DAD)
        db.session.add_all([admin_user, parent, SiteDetails(email='c@t.com')])
        db.session.commit()
        self._login(client, 'admin', 'pw')

        # Mock the return value for the main responsive image upload
        mock_upload.side_effect = [
            {
                'original': 'parents/main-original.jpg',
                'large': 'parents/main-large.jpg',
                'medium': 'parents/main-medium.jpg',
                'small': 'parents/main-small.jpg'
            },
            'parents_alternates/alt1.jpg' # Return value for the alternate image
        ]
        
        main_image = (io.BytesIO(b"fake main image"), 'main.jpg')
        alt_image = (io.BytesIO(b"fake alt image"), 'alternate1.jpg')

        response = client.post(
            url_for('parent.edit_view', id=parent.id),
            data={
                'name': 'New Name',
                'role': 'DAD',
                'image_upload': main_image,
                'alternate_image_upload_1': alt_image
            },
            content_type='multipart/form-data',
            follow_redirects=True
        )

        assert response.status_code == 200
        db.session.refresh(parent)
        
        assert parent.name == 'New Name'
        assert parent.main_image_s3_key == 'parents/main-original.jpg'
        assert parent.main_image_s3_key_large == 'parents/main-large.jpg'
        assert parent.alternate_image_s3_key_1 == 'parents_alternates/alt1.jpg'
        assert mock_upload.call_count == 2