# tests/test_announcement_admin_bs5.py

import pytest
from flask import url_for
from bs4 import BeautifulSoup
from app.models import User, AnnouncementBanner, Puppy, Parent, ParentRole, SiteMeta, db
from datetime import date

class TestAdminAnnouncementBS5:
    """
    Test suite for the new Bootstrap 5 implementation of the Announcement Banner admin panel.
    This ensures that the new templates, view logic, and form handling work correctly.
    """

    @pytest.fixture(autouse=True)
    def setup_and_login(self, client, db):
        """
        Fixture to create a clean database, add necessary data (admin user, parents, puppy),
        and log in the client before each test.
        """
        admin_user = User(username='admin')
        admin_user.set_password('password')
        db.session.add(admin_user)
        
        mom = Parent(name='Test Mom', role=ParentRole.MOM)
        dad = Parent(name='Test Dad', role=ParentRole.DAD)
        db.session.add_all([mom, dad])
        db.session.commit()

        self.puppy1 = Puppy(name='Featured Puppy', birth_date=date(2025, 1, 1), mom_id=mom.id, dad_id=dad.id)
        db.session.add(self.puppy1)
        db.session.add(SiteMeta(email='contact@test.com'))
        db.session.commit()

        client.post(
            url_for('admin_auth.login'),
            data={'username': 'admin', 'password': 'password'},
            follow_redirects=True
        )
        yield client

    def test_full_banner_crud_workflow_bs5(self, setup_and_login, db):
        """
        Tests the complete CREATE, READ, UPDATE, and DELETE lifecycle for an
        AnnouncementBanner record using the new Bootstrap 5 views.
        """
        client = setup_and_login

        # 1. CREATE
        create_response = client.post(
            url_for('announcementbanner.create_view'),
            data={
                'main_text': 'New Litter Available!',
                'sub_text': 'A beautiful new litter from {mom_name} & {dad_name}.',
                'button_text': 'Meet Them',
                'is_active': 'y',
                'featured_puppy': self.puppy1.id
            },
            follow_redirects=True
        )
        assert b'Record was successfully created.' in create_response.data
        banner = AnnouncementBanner.query.filter_by(main_text='New Litter Available!').first()
        assert banner is not None
        assert banner.is_active is True
        assert banner.featured_puppy_id == self.puppy1.id

        # 2. READ
        list_response = client.get(url_for('announcementbanner.index_view'))
        assert list_response.status_code == 200
        assert b'New Litter Available!' in list_response.data

        # 3. UPDATE
        edit_response = client.post(
            url_for('announcementbanner.edit_view', id=banner.id),
            data={
                'main_text': 'New Litter (Updated)',
                'sub_text': banner.sub_text,
                'button_text': banner.button_text,
                'is_active': '',
                'featured_puppy': self.puppy1.id
            },
            follow_redirects=True
        )
        assert b'Record was successfully saved.' in edit_response.data
        db.session.refresh(banner)
        assert banner.main_text == 'New Litter (Updated)'
        assert banner.is_active is False

        # 4. DELETE
        delete_response = client.post(
            url_for('announcementbanner.delete_view', id=banner.id),
            data={'id': banner.id},
            follow_redirects=True
        )
        assert b'Record was successfully deleted.' in delete_response.data
        assert db.session.get(AnnouncementBanner, banner.id) is None

    def test_announcement_edit_view_loads_live_preview(self, setup_and_login, db):
        """
        Confirms that the edit view correctly loads the live preview HTML structure
        and that all necessary elements have their required IDs for JavaScript to function.
        """
        client = setup_and_login
        # Create a banner to edit
        banner = AnnouncementBanner(main_text="Test Banner", button_text="Click Me", featured_puppy_id=self.puppy1.id)
        db.session.add(banner)
        db.session.commit()

        response = client.get(url_for('announcementbanner.edit_view', id=banner.id))
        assert response.status_code == 200
        soup = BeautifulSoup(response.data, 'html.parser')

        # 1. Check for the main preview container
        preview_container = soup.find('div', class_='live-preview-container')
        assert preview_container is not None, "The live-preview-container div is missing."
        assert preview_container.find('h3').text == "Live Preview"

        # 2. Check for the specific preview wrapper with its ID
        wrapper = preview_container.find('div', id='banner-preview-wrapper')
        assert wrapper is not None, "The banner-preview-wrapper div is missing."

        # 3. Verify that all preview elements have their required IDs
        assert wrapper.find('h4', id='preview-main-text') is not None
        assert wrapper.find('p', id='preview-sub-text') is not None
        assert wrapper.find('a', id='preview-button-text') is not None

        # 4. Verify that the form inputs have IDs for the JavaScript to target
        assert soup.find('input', id='main_text') is not None
        assert soup.find('input', id='sub_text') is not None
        assert soup.find('input', id='button_text') is not None
        assert soup.find('select', id='featured_puppy') is not None