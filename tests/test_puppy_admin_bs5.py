# tests/test_puppy_admin_bs5.py

import pytest
import io
from unittest.mock import patch
from flask import url_for
from bs4 import BeautifulSoup
from app.models import User, Puppy, Parent, ParentRole, SiteDetails, db
from datetime import date

class TestAdminPuppyBS5:
    """
    Test suite for the Bootstrap 5 implementation of the Puppy admin panel.
    """

    @pytest.fixture(autouse=True)
    def setup_and_login(self, client, db):
        """
        Sets up the database with necessary records (admin, parents) and logs in the client.
        This runs automatically for each test in this class.
        """
        admin_user = User(username='admin')
        admin_user.set_password('password')
        db.session.add(admin_user)

        self.mom = Parent(name='Test Mom', role=ParentRole.MOM, is_active=True)
        self.dad = Parent(name='Test Dad', role=ParentRole.DAD, is_active=True)
        db.session.add_all([self.mom, self.dad])
        db.session.add(SiteDetails(email='contact@test.com'))
        db.session.commit()

        client.post(
            url_for('admin_auth.login'),
            data={'username': 'admin', 'password': 'password'},
            follow_redirects=True
        )
        yield client

    @patch('app.routes.admin.views.puppy_views.upload_image', return_value='puppies/mock-puppy.jpg')
    def test_full_puppy_crud_workflow_bs5(self, mock_upload_image, setup_and_login, db):
        """
        Tests the complete CREATE, READ, UPDATE, and DELETE lifecycle for a Puppy
        record using the new Bootstrap 5 views.
        """
        client = setup_and_login

        # 1. CREATE
        create_response = client.post(
            url_for('puppy.create_view'),
            data={
                'name': 'Buddy',
                'birth_date': '2025-01-01',
                'status': 'AVAILABLE',
                'mom_id': self.mom.id,
                'dad_id': self.dad.id,
                'image_upload': (io.BytesIO(b"fake-image"), 'buddy.jpg')
            },
            content_type='multipart/form-data',
            follow_redirects=True
        )
        assert b'Record was successfully created.' in create_response.data
        puppy = Puppy.query.filter_by(name='Buddy').first()
        assert puppy is not None
        assert puppy.mom == self.mom
        assert puppy.main_image_s3_key == 'puppies/mock-puppy.jpg'
        mock_upload_image.assert_called_once()

        # 2. READ
        list_response = client.get(url_for('puppy.index_view'))
        assert list_response.status_code == 200
        assert b'Buddy' in list_response.data

        # 3. UPDATE
        edit_response = client.post(
            url_for('puppy.edit_view', id=puppy.id),
            data={
                'name': 'Buddy Updated',
                'birth_date': '2025-01-02',
                'status': 'RESERVED',
                'mom_id': self.mom.id,
                'dad_id': self.dad.id
            },
            follow_redirects=True
        )
        assert b'Record was successfully saved.' in edit_response.data
        db.session.refresh(puppy)
        assert puppy.name == 'Buddy Updated'
        assert str(puppy.birth_date) == '2025-01-02'

        # 4. DELETE
        delete_response = client.post(
            url_for('puppy.delete_view', id=puppy.id),
            data={'id': puppy.id},
            follow_redirects=True
        )
        assert b'Record was successfully deleted.' in delete_response.data
        assert db.session.get(Puppy, puppy.id) is None

    def test_puppy_edit_view_loads_live_preview_bs5(self, setup_and_login, db):
        """
        Confirms the edit view loads the live preview HTML structure and that all
        necessary elements have IDs for the JavaScript preview to function.
        """
        client = setup_and_login
        puppy = Puppy(name='Test Puppy', birth_date=date(2025, 5, 5), mom_id=self.mom.id, dad_id=self.dad.id)
        db.session.add(puppy)
        db.session.commit()

        response = client.get(url_for('puppy.edit_view', id=puppy.id))
        assert response.status_code == 200
        soup = BeautifulSoup(response.data, 'html.parser')

        # Check for the main preview container and its elements
        preview_container = soup.find('div', class_='live-preview-container')
        assert preview_container is not None
        assert preview_container.find('h3').text == "Live Preview"
        assert preview_container.find('img', id='preview-puppy-image') is not None
        assert preview_container.find('h5', id='preview-puppy-name') is not None
        assert preview_container.find('span', id='preview-mom-name') is not None
        assert preview_container.find('span', id='preview-dad-name') is not None
        assert preview_container.find('span', id='preview-puppy-status') is not None

        # Check that form inputs have the correct IDs
        assert soup.find('input', id='name') is not None
        assert soup.find('select', id='mom_id') is not None
        assert soup.find('select', id='dad_id') is not None