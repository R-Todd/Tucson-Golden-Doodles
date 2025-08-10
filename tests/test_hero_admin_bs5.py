# tests/test_hero_admin_bs5.py

import pytest
import io
from unittest.mock import patch
from flask import url_for
from bs4 import BeautifulSoup
from app.models import User, HeroSection, SiteMeta, db

class TestAdminHeroBS5:
    """
    Test suite for the new Bootstrap 5 implementation of the Hero Section admin.
    This ensures that the new templates and view logic work correctly and are
    properly isolated from the old BS4 implementation.
    """

    @pytest.fixture(autouse=True)
    def setup_and_login(self, client, db):
        """
        Fixture to create a clean database, add a SiteMeta record,
        create an admin user, and log them in before each test.
        """
        admin_user = User(username='admin')
        admin_user.set_password('password')
        # A SiteMeta record is often needed for the base template to render
        db.session.add(SiteMeta(email='contact@test.com'))
        db.session.add(admin_user)
        db.session.commit()

        client.post(
            url_for('admin_auth.login'),
            data={'username': 'admin', 'password': 'password'},
            follow_redirects=True
        )
        # Yield the authenticated client to the tests
        yield client

    @patch('app.routes.admin.views.home.hero_view.upload_image', return_value={'original': 'hero/mock-image.jpg'})
    def test_full_hero_crud_workflow_bs5(self, mock_upload_image, setup_and_login, db):
        """
        Tests the complete CREATE, READ, UPDATE, and DELETE lifecycle of a
        HeroSection record using the dedicated Bootstrap 5 views.
        """
        client = setup_and_login

        # 1. CREATE: Post data to the create view
        create_response = client.post(
            url_for('herosection.create_view'),
            data={
                'main_title': 'Initial Hero Title',
                'subtitle': 'The Subtitle',
                'description': 'A great description.',
                'image_upload': (io.BytesIO(b"fake-image-data"), 'test.jpg')
            },
            content_type='multipart/form-data',
            follow_redirects=True
        )
        assert b'Record was successfully created.' in create_response.data
        hero = HeroSection.query.filter_by(main_title='Initial Hero Title').first()
        assert hero is not None
        assert hero.description == 'A great description.'
        mock_upload_image.assert_called_once() # Verify the mock uploader was triggered

        # 2. READ: Check the list view for the new record
        list_response = client.get(url_for('herosection.index_view'))
        assert list_response.status_code == 200
        assert b'Initial Hero Title' in list_response.data
        assert b'The Subtitle' in list_response.data

        # 3. UPDATE: Edit the newly created record
        edit_response = client.post(
            url_for('herosection.edit_view', id=hero.id),
            data={'main_title': 'Updated Hero Title', 'subtitle': 'Updated Subtitle'},
            follow_redirects=True
        )
        assert b'Record was successfully saved.' in edit_response.data
        db.session.refresh(hero)
        assert hero.main_title == 'Updated Hero Title'

        # 4. DELETE: Remove the record
        delete_response = client.post(
            url_for('herosection.delete_view', id=hero.id),
            data={'id': hero.id}, # The form inside the BS5 modal sends the ID
            follow_redirects=True
        )
        assert b'Record was successfully deleted.' in delete_response.data
        deleted_hero = db.session.get(HeroSection, hero.id)
        assert deleted_hero is None

    def test_hero_edit_view_loads_bs5_template(self, setup_and_login, db):
        """
        Confirms that the edit view is loading the correct BS5 template by
        checking for a class that is specific to our BS5 implementation.
        """
        client = setup_and_login
        hero = HeroSection(main_title='Test')
        db.session.add(hero)
        db.session.commit()

        response = client.get(url_for('herosection.edit_view', id=hero.id))
        soup = BeautifulSoup(response.data, 'html.parser')

        # The 'container' class with a 'mt-4' margin is unique to our BS5 templates
        form_container = soup.find('div', class_='container mt-4')
        assert form_container is not None, \
            "The view did not load the Bootstrap 5 template with the correct container."