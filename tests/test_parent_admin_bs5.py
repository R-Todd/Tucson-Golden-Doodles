# tests/test_parent_admin_bs5.py

import pytest
import io
from unittest.mock import patch
from flask import url_for
from bs4 import BeautifulSoup
from app.models import User, Parent, ParentRole, SiteMeta, db

class TestAdminParentBS5:
    """
    Test suite for the new Bootstrap 5 implementation of the Parent admin panel.
    This ensures the new templates are isolated and all functionality works as expected.
    """

    @pytest.fixture(autouse=True)
    def setup_and_login(self, client, db):
        """
        Fixture to create a clean database, add essential site metadata,
        create an admin user, and log them in before each test.
        """
        admin_user = User(username='admin')
        admin_user.set_password('password')
        db.session.add(SiteMeta(email='contact@test.com'))
        db.session.add(admin_user)
        db.session.commit()

        client.post(
            url_for('admin_auth.login'),
            data={'username': 'admin', 'password': 'password'},
            follow_redirects=True
        )
        yield client

    @patch('app.routes.admin.views.parent_views.upload_image')
    def test_full_parent_crud_workflow_bs5(self, mock_upload_image, setup_and_login, db):
        """
        Tests the complete CREATE, READ, UPDATE, and DELETE lifecycle for a Parent
        record using the dedicated Bootstrap 5 views.
        """
        client = setup_and_login

        # Mock the S3 uploader to return predictable keys
        mock_upload_image.side_effect = [
            {'original': 'parents/main.jpg', 'large': 'parents/main-large.jpg'},
            'parents_alternates/alt1.jpg'
        ]

        # 1. CREATE
        create_response = client.post(
            url_for('parent.create_view'),
            data={
                'name': 'Archie',
                'role': 'DAD',
                'breed': 'F1 Mini Poodle',
                'description': 'A wonderful sire.',
                'image_upload': (io.BytesIO(b"fake-main-image"), 'main.jpg'),
                'alternate_image_upload_1': (io.BytesIO(b"fake-alt-image"), 'alt1.jpg')
            },
            content_type='multipart/form-data',
            follow_redirects=True
        )
        assert b'Record was successfully created.' in create_response.data
        parent = Parent.query.filter_by(name='Archie').first()
        assert parent is not None
        assert parent.breed == 'F1 Mini Poodle'
        assert parent.main_image_s3_key == 'parents/main.jpg'
        assert parent.alternate_image_s3_key_1 == 'parents_alternates/alt1.jpg'
        assert mock_upload_image.call_count == 2

        # 2. READ
        list_response = client.get(url_for('parent.index_view'))
        assert list_response.status_code == 200
        assert b'Archie' in list_response.data

        # 3. UPDATE
        edit_response = client.post(
            url_for('parent.edit_view', id=parent.id),
            data={'name': 'Archie Updated', 'role': 'DAD', 'breed': 'Poodle'},
            follow_redirects=True
        )
        assert b'Record was successfully saved.' in edit_response.data
        db.session.refresh(parent)
        assert parent.name == 'Archie Updated'

        # 4. DELETE
        delete_response = client.post(
            url_for('parent.delete_view', id=parent.id),
            data={'id': parent.id},
            follow_redirects=True
        )
        assert b'Record was successfully deleted.' in delete_response.data
        assert db.session.get(Parent, parent.id) is None

    def test_parent_edit_view_loads_bs5_and_live_preview(self, setup_and_login, db):
        """
        Confirms the parent edit view loads the correct BS5 template and that all
        live preview elements and form inputs have their necessary IDs.
        """
        client = setup_and_login
        parent = Parent(name='Test Parent', role=ParentRole.MOM, breed='Goldendoodle')
        db.session.add(parent)
        db.session.commit()

        response = client.get(url_for('parent.edit_view', id=parent.id))
        assert response.status_code == 200
        soup = BeautifulSoup(response.data, 'html.parser')

        # Verify it's a BS5 template by checking for a BS5-specific class
        assert soup.find('div', class_='container-fluid mt-4') is not None
        
        # Verify live preview container and its elements
        preview_container = soup.find('div', class_='live-preview-container')
        assert preview_container is not None
        assert preview_container.find('h1', id='preview-parent-name') is not None
        assert preview_container.find('img', id='preview-parent-image') is not None
        assert preview_container.find('h3', id='preview-parent-breed') is not None
        
        # Verify form inputs have IDs for JavaScript
        assert soup.find('input', id='name') is not None
        assert soup.find('select', id='role') is not None
        assert soup.find('input', id='breed') is not None
        assert soup.find('textarea', id='description') is not None
        assert soup.find('input', id='image_upload') is not None
        assert soup.find('input', id='alternate_image_upload_1') is not None