# tests/test_about_admin_bs5.py

import pytest
import io
from unittest.mock import patch
from flask import url_for
from bs4 import BeautifulSoup
from app.models import User, AboutSection, SiteMeta, db

class TestAdminAboutBS5:
    """
    Test suite for the Bootstrap 5 implementation of the About Section admin panel.
    It verifies CRUD functionality and the presence of the live preview feature.
    """

    @pytest.fixture(autouse=True)
    def setup_and_login(self, client, db):
        """
        Fixture to create a clean database, add essential site metadata,
        create an admin user, and log them in before each test.
        """
        admin_user = User(username='admin')
        admin_user.set_password('password')
        # A SiteMeta record is needed for the base template to render.
        db.session.add(SiteMeta(email='contact@test.com'))
        db.session.add(admin_user)
        db.session.commit()

        # Log in the client.
        client.post(
            url_for('admin_auth.login'),
            data={'username': 'admin', 'password': 'password'},
            follow_redirects=True
        )
        yield client # Provide the authenticated client to the tests.

    @patch('app.routes.admin.views.home.about_view.upload_image', return_value={'original': 'about/mock-image.jpg'})
    def test_full_about_crud_workflow_bs5(self, mock_upload_image, setup_and_login, db):
        """
        Tests the complete CREATE, READ, UPDATE, and DELETE lifecycle for an
        AboutSection record using the dedicated Bootstrap 5 views.
        """
        client = setup_and_login

        # 1. CREATE: Post data to the create view to make a new record.
        create_response = client.post(
            url_for('aboutsection.create_view'),
            data={
                'title': 'Initial About Title',
                'content_html': '<p>Original content.</p>',
                'image_upload': (io.BytesIO(b"fake-image-data"), 'test.jpg')
            },
            content_type='multipart/form-data',
            follow_redirects=True
        )
        assert b'Record was successfully created.' in create_response.data
        about = AboutSection.query.filter_by(title='Initial About Title').first()
        assert about is not None
        assert about.content_html == '<p>Original content.</p>'
        mock_upload_image.assert_called_once() # Ensure the image uploader was called.

        # 2. READ: Check the list view to see the new record.
        list_response = client.get(url_for('aboutsection.index_view'))
        assert list_response.status_code == 200
        assert b'Initial About Title' in list_response.data

        # 3. UPDATE: Edit the record with new data.
        edit_response = client.post(
            url_for('aboutsection.edit_view', id=about.id),
            data={'title': 'Updated About Title', 'content_html': '<p>Updated content.</p>'},
            follow_redirects=True
        )
        assert b'Record was successfully saved.' in edit_response.data
        db.session.refresh(about)
        assert about.title == 'Updated About Title'

        # 4. DELETE: Remove the record using the delete view.
        # Note: The 'About' list view doesn't have a delete button, but the view still exists.
        delete_response = client.post(
            url_for('aboutsection.delete_view', id=about.id),
            data={'id': about.id},
            follow_redirects=True
        )
        assert b'Record was successfully deleted.' in delete_response.data
        deleted_about = db.session.get(AboutSection, about.id)
        assert deleted_about is None

    def test_about_edit_view_loads_bs5_and_preview(self, setup_and_login, db):
        """
        Confirms that the edit view loads the correct BS5 template and that all
        elements required for the live preview (containers, element IDs) are present.
        """
        client = setup_and_login
        # Create an AboutSection record to edit.
        about = AboutSection(title='Test About', content_html='<p>Content</p>', image_s3_key='about/test.jpg')
        db.session.add(about)
        db.session.commit()

        response = client.get(url_for('aboutsection.edit_view', id=about.id))
        assert response.status_code == 200
        soup = BeautifulSoup(response.data, 'html.parser')

        # Verify BS5 template is loaded by checking for our specific container class.
        assert soup.find('div', class_='container mt-4') is not None, "Did not load the BS5 container."

        # Verify the live preview container and its wrapper exist.
        preview_container = soup.find('div', class_='live-preview-container')
        assert preview_container is not None, "The live-preview-container div is missing."
        assert preview_container.find('div', id='about-preview-wrapper') is not None

        # Verify that all preview elements have their required IDs.
        assert preview_container.find('h2', id='preview-about-title') is not None
        assert preview_container.find('div', id='preview-about-content') is not None
        assert preview_container.find('img', id='preview-about-image') is not None

        # Verify that the form inputs have IDs for the JavaScript to target.
        assert soup.find('input', id='about_title') is not None
        assert soup.find('textarea', id='about_content_html') is not None