# tests/test_gallery_admin_bs5.py

import pytest
import io
from unittest.mock import patch
from flask import url_for
from bs4 import BeautifulSoup
from app.models import User, GalleryImage, SiteDetails, db

class TestAdminGalleryBS5:
    """
    Test suite for the Bootstrap 5 implementation of the Gallery Images admin panel.
    """

    @pytest.fixture(autouse=True)
    def setup_and_login(self, client, db):
        """ Fixture to set up a clean database and log in an admin user. """
        admin_user = User(username='admin')
        admin_user.set_password('password')
        db.session.add(SiteDetails(email='contact@test.com'))
        db.session.add(admin_user)
        db.session.commit()

        client.post(
            url_for('admin_auth.login'),
            data={'username': 'admin', 'password': 'password'},
            follow_redirects=True
        )
        yield client

    @patch('app.routes.admin.views.home.gallery_view.upload_image', return_value='gallery/mock-image.jpg')
    def test_full_gallery_crud_workflow_bs5(self, mock_upload_image, setup_and_login, db):
        """
        Tests the complete CREATE, READ, UPDATE, and DELETE lifecycle for a
        GalleryImage record using the dedicated Bootstrap 5 views.
        """
        client = setup_and_login

        # 1. CREATE
        create_response = client.post(
            url_for('galleryimage.create_view'),
            data={
                'caption': 'A beautiful puppy.',
                'sort_order': '10',
                'image_upload': (io.BytesIO(b"fake-image-data"), 'test.jpg')
            },
            content_type='multipart/form-data',
            follow_redirects=True
        )
        assert b'Record was successfully created.' in create_response.data
        image = GalleryImage.query.filter_by(caption='A beautiful puppy.').first()
        assert image is not None
        assert image.sort_order == 10
        assert image.image_s3_key == 'gallery/mock-image.jpg'
        mock_upload_image.assert_called_once()

        # 2. READ
        list_response = client.get(url_for('galleryimage.index_view'))
        assert list_response.status_code == 200
        assert b'A beautiful puppy.' in list_response.data

        # 3. UPDATE
        edit_response = client.post(
            url_for('galleryimage.edit_view', id=image.id),
            data={'caption': 'An updated caption.', 'sort_order': '5'},
            follow_redirects=True
        )
        assert b'Record was successfully saved.' in edit_response.data
        db.session.refresh(image)
        assert image.caption == 'An updated caption.'
        assert image.sort_order == 5

        # 4. DELETE
        delete_response = client.post(
            url_for('galleryimage.delete_view', id=image.id),
            data={'id': image.id},
            follow_redirects=True
        )
        assert b'Record was successfully deleted.' in delete_response.data
        assert db.session.get(GalleryImage, image.id) is None

    def test_gallery_edit_view_loads_live_preview(self, setup_and_login, db):
        """
        Confirms the edit view correctly loads the live preview HTML structure
        and that all necessary elements have IDs for JavaScript to function.
        """
        client = setup_and_login
        image = GalleryImage(caption='Test Image', image_s3_key='gallery/test.jpg', sort_order=1)
        db.session.add(image)
        db.session.commit()

        response = client.get(url_for('galleryimage.edit_view', id=image.id))
        assert response.status_code == 200
        soup = BeautifulSoup(response.data, 'html.parser')

        # Check for the main preview container
        preview_container = soup.find('div', class_='live-preview-container')
        assert preview_container is not None
        assert preview_container.find('h3').text == "Live Preview"

        # Verify that all preview elements have their required IDs
        assert preview_container.find('img', id='preview-gallery-image') is not None
        assert preview_container.find('p', id='preview-gallery-caption') is not None

        # Verify that the form inputs have IDs for the JavaScript to target
        assert soup.find('input', id='caption') is not None
        assert soup.find('input', id='sort_order') is not None