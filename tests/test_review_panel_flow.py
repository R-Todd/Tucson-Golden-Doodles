# tests/test_review_panel_flow.py

import pytest
from flask import url_for
from bs4 import BeautifulSoup
from app.models import User, Review, SiteMeta, db

class TestAdminReviewWorkflow:
    """
    A complete test suite to verify the entire admin workflow for managing reviews,
    from the dashboard link to creating, editing, and deleting records.
    """

    @pytest.fixture(autouse=True)
    def setup(self, client, db):
        """
        This fixture automatically runs before each test in this class.
        It creates and logs in an admin user, ensuring an authenticated state.
        """
        admin_user = User(username='admin')
        admin_user.set_password('password')
        # SiteMeta is often required for base templates to render
        db.session.add(SiteMeta(email='contact@test.com'))
        db.session.add(admin_user)
        db.session.commit()

        client.post(
            url_for('admin_auth.login'),
            data={'username': 'admin', 'password': 'password'},
            follow_redirects=True
        )
        # Yield the client to the test function
        yield client

    def test_dashboard_link_leads_to_reviews_page(self, setup):
        """
        1. Verifies the 'Manage Customer Reviews' link on the dashboard.
        GIVEN an authenticated admin on the dashboard
        WHEN the dashboard page is requested
        THEN check that the 'View Reviews' link points to the correct review admin page.
        """
        client = setup
        response = client.get(url_for('admin.index'))
        assert response.status_code == 200

        soup = BeautifulSoup(response.data, 'html.parser')
        
        # Find the link by its href pointing to the review index view
        review_link = soup.find('a', href=url_for('review.index_view'))
        
        assert review_link is not None, "The 'View Reviews' link is missing from the dashboard."
        assert 'Manage Customer Reviews' in review_link.find_previous('h5').text, "The card title for the review link is incorrect."
        assert review_link.text == 'View Reviews'

    def test_review_list_page_loads_and_has_correct_actions(self, setup, db):
        """
        2. Verifies the Review List page itself.
        GIVEN an authenticated admin
        WHEN the review list page is requested
        THEN check it loads Bootstrap 5 and has 'Create', 'Edit', and 'Delete' actions.
        """
        client = setup
        # Add a review to ensure the action buttons are rendered
        db.session.add(Review(author_name='Initial Author', testimonial_text='Some text.'))
        db.session.commit()

        response = client.get(url_for('review.index_view'))
        assert response.status_code == 200
        soup = BeautifulSoup(response.data, 'html.parser')

        # Check for Bootstrap 5
        assert soup.find('link', href=lambda x: x and 'bootstrap@5' in x), "Bootstrap 5 CSS is not loaded."

        # Check for action buttons
        assert soup.find('a', href=url_for('review.create_view')), "The 'Create' button is missing."
        assert soup.find('a', href=lambda x: x and 'review/edit' in x), "The 'Edit' button is missing."
        assert soup.find('form', action=lambda x: x and 'review/delete' in x), "The 'Delete' form action is missing."

    def test_create_and_edit_review_workflow(self, setup, db):
        """
        3. Verifies the Create and Edit functionality in a single workflow.
        GIVEN an authenticated admin
        WHEN a new review is created and then subsequently edited
        THEN check that the data is correctly saved to the database at each step.
        """
        client = setup
        
        # --- Step 1: Create the Review ---
        create_response = client.post(
            url_for('review.create_view'),
            data={
                'author_name': 'Original Author',
                'testimonial_text': 'Original testimonial.',
                'is_featured': 'y'
            },
            follow_redirects=True
        )
        assert b'Record was successfully created.' in create_response.data
        
        # Verify creation in the database
        review = Review.query.filter_by(author_name='Original Author').first()
        assert review is not None
        assert review.testimonial_text == 'Original testimonial.'
        assert review.is_featured is True

        # --- Step 2: Edit the Same Review ---
        edit_response = client.post(
            url_for('review.edit_view', id=review.id),
            data={
                'author_name': 'Updated Author',
                'testimonial_text': 'This text has been updated.',
                'is_featured': ''  # Uncheck the box
            },
            follow_redirects=True
        )
        assert b'Record was successfully saved.' in edit_response.data

        # Verify the update in the database
        db.session.refresh(review)
        assert review.author_name == 'Updated Author'
        assert review.testimonial_text == 'This text has been updated.'
        assert review.is_featured is False

    def test_delete_review_removes_from_database(self, setup, db):
        """
        4. Verifies the Delete functionality.
        GIVEN an authenticated admin and an existing review
        WHEN the review is deleted
        THEN check that it is fully removed from the database.
        """
        client = setup
        review_to_delete = Review(author_name='ToBeDeleted', testimonial_text='Delete this.')
        db.session.add(review_to_delete)
        db.session.commit()
        review_id = review_to_delete.id

        # --- Delete the record ---
        delete_response = client.post(
            url_for('review.delete_view', id=review_id),
            follow_redirects=True
        )
        assert b'Record was successfully deleted.' in delete_response.data

        # Verify deletion from the database
        deleted_review = db.session.get(Review, review_id)
        assert deleted_review is None, "The review was not deleted from the database."