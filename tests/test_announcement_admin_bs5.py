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
        # Create an admin user and log them in
        admin_user = User(username='admin')
        admin_user.set_password('password')
        db.session.add(admin_user)
        
        # Create necessary parent and puppy data for the form's QuerySelectField
        mom = Parent(name='Test Mom', role=ParentRole.MOM)
        dad = Parent(name='Test Dad', role=ParentRole.DAD)
        db.session.add_all([mom, dad])
        db.session.commit() # Commit parents to get their IDs

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

        # 1. CREATE: Post data to the create view to make a new banner
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

        # 2. READ: Check the list view for the newly created record
        list_response = client.get(url_for('announcementbanner.index_view'))
        assert list_response.status_code == 200
        assert b'New Litter Available!' in list_response.data

        # 3. UPDATE: Edit the banner to deactivate it
        edit_response = client.post(
            url_for('announcementbanner.edit_view', id=banner.id),
            data={
                'main_text': 'New Litter (Updated)',
                'sub_text': banner.sub_text,
                'button_text': banner.button_text,
                'is_active': '', # Unchecking the 'is_active' box
                'featured_puppy': self.puppy1.id
            },
            follow_redirects=True
        )
        assert b'Record was successfully saved.' in edit_response.data
        db.session.refresh(banner)
        assert banner.main_text == 'New Litter (Updated)'
        assert banner.is_active is False

        # 4. DELETE: Remove the banner record
        delete_response = client.post(
            url_for('announcementbanner.delete_view', id=banner.id),
            data={'id': banner.id},
            follow_redirects=True
        )
        assert b'Record was successfully deleted.' in delete_response.data
        deleted_banner = db.session.get(AnnouncementBanner, banner.id)
        assert deleted_banner is None

    def test_banner_view_loads_bs5_template(self, setup_and_login, db):
        """
        Confirms that the create view is loading the correct BS5 template by
        checking for a class that is specific to our BS5 implementation.
        """
        client = setup_and_login
        response = client.get(url_for('announcementbanner.create_view'))
        soup = BeautifulSoup(response.data, 'html.parser')

        # The 'container' with a 'mt-4' margin is unique to our BS5 templates
        form_container = soup.find('div', class_='container mt-4')
        assert form_container is not None, "The view did not load the Bootstrap 5 template."