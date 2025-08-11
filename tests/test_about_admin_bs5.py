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
    It verifies CRUD functionality and the presence of the live preview feature,
    including the CKEditor integration.
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

    @patch('app.routes.admin.views.home.about_view.upload_image', return_value={'original': 'about/mock-image.jpg'})
    def test_full_about_crud_workflow_bs5(self, mock_upload_image, setup_and_login, db):
        """
        Tests the complete CREATE, READ, UPDATE, and DELETE lifecycle for an
        AboutSection record using the dedicated Bootstrap 5 views.
        """
        client = setup_and_login

        # 1. CREATE
        create_response = client.post(
            url_for('aboutsection.create_view'),
            data={
                'title': 'Initial About Title',
                'content_html': '<p>Original content with <b>bold</b>.</p>',
                'image_upload': (io.BytesIO(b"fake-image-data"), 'test.jpg')
            },
            content_type='multipart/form-data',
            follow_redirects=True
        )
        assert b'Record was successfully created.' in create_response.data
        about = AboutSection.query.filter_by(title='Initial About Title').first()
        assert about is not None
        assert about.content_html == '<p>Original content with <b>bold</b>.</p>'
        mock_upload_image.assert_called_once()

        # 2. READ
        list_response = client.get(url_for('aboutsection.index_view'))
        assert list_response.status_code == 200
        assert b'Initial About Title' in list_response.data

        # 3. UPDATE
        edit_response = client.post(
            url_for('aboutsection.edit_view', id=about.id),
            data={'title': 'Updated Title', 'content_html': '<p>Updated content.</p>'},
            follow_redirects=True
        )
        assert b'Record was successfully saved.' in edit_response.data
        db.session.refresh(about)
        assert about.title == 'Updated Title'

        # 4. DELETE
        delete_response = client.post(
            url_for('aboutsection.delete_view', id=about.id),
            data={'id': about.id},
            follow_redirects=True
        )
        assert b'Record was successfully deleted.' in delete_response.data
        assert db.session.get(AboutSection, about.id) is None

    def test_about_edit_view_loads_ckeditor_and_preview(self, setup_and_login, db):
        """
        Confirms the edit view is set up for CKEditor by checking for
        the target textarea and the necessary script tag.
        """
        client = setup_and_login
        about = AboutSection(title='Test About', content_html='<p>Content</p>', image_s3_key='about/test.jpg')
        db.session.add(about)
        db.session.commit()

        response = client.get(url_for('aboutsection.edit_view', id=about.id))
        assert response.status_code == 200
        soup = BeautifulSoup(response.data, 'html.parser')

        # --- THIS IS THE FIX ---
        # 1. Verify that the target TEXTAREA for CKEditor exists.
        textarea = soup.find('textarea', id='content_html')
        assert textarea is not None, "The target textarea for CKEditor is missing."

        # 2. Verify that the script to load CKEditor is included in the page.
        ckeditor_script = soup.find('script', src=lambda s: s and 'cdn.ckeditor.com' in s)
        assert ckeditor_script is not None, "The CKEditor script tag was not found in the HTML."
        # --- END OF FIX ---

        # 3. Verify the live preview elements are still present.
        preview_container = soup.find('div', class_='live-preview-container')
        assert preview_container is not None
        assert preview_container.find('h2', id='preview-about-title') is not None
        assert preview_container.find('div', id='preview-about-content') is not None
        assert preview_container.find('img', id='preview-about-image') is not None