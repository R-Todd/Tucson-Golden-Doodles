# tests/test_review_admin_comprehensive.py

import pytest
from flask import url_for
from bs4 import BeautifulSoup
from app.models import User, Review, SiteMeta, db

class TestAdminReviewComprehensive:
    """
    A detailed test suite to verify all functionality of the review admin panel,
    including single-record lifecycle and multi-record management.
    """

    @pytest.fixture(autouse=True)
    def setup_and_login(self, client, db):
        """
        Fixture to create and log in an admin user before each test.
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

    def test_full_review_crud_workflow(self, setup_and_login, db):
        """
        Tests the complete lifecycle of a single review:
        1. CREATE a new review.
        2. READ it from the list view.
        3. UPDATE (Edit) the review.
        4. DELETE the review.
        """
        client = setup_and_login

        # 1. CREATE the review
        create_response = client.post(
            url_for('review.create_view'),
            data={
                'author_name': 'Original Author',
                'testimonial_text': 'This is the original review.',
                'is_featured': 'y'
            },
            follow_redirects=True
        )
        assert b'Record was successfully created.' in create_response.data
        review = Review.query.filter_by(author_name='Original Author').first()
        assert review is not None
        assert review.is_featured is True

        # 2. READ the review from the list page
        list_response = client.get(url_for('review.index_view'))
        assert b'Original Author' in list_response.data
        assert b'This is the original review.' in list_response.data

        # 3. UPDATE (Edit) the review
        edit_response = client.post(
            url_for('review.edit_view', id=review.id),
            data={
                'author_name': 'Updated Author',
                'testimonial_text': 'The review has been updated.',
                'is_featured': ''  # Uncheck the 'is_featured' box
            },
            follow_redirects=True
        )
        assert b'Record was successfully saved.' in edit_response.data
        db.session.refresh(review)
        assert review.author_name == 'Updated Author'
        assert review.testimonial_text == 'The review has been updated.'
        assert review.is_featured is False

        # 4. DELETE the review
        delete_response = client.post(
            url_for('review.delete_view', id=review.id),
            data={'id': review.id}, # Send ID in form body
            follow_redirects=True
        )
        assert b'Record was successfully deleted.' in delete_response.data
        deleted_review = db.session.get(Review, review.id)
        assert deleted_review is None

    def test_managing_multiple_reviews(self, setup_and_login, db):
        """
        Tests that actions on one review do not affect others.
        """
        client = setup_and_login

        review1 = Review(author_name='Author One', testimonial_text='First review.')
        review2 = Review(author_name='Author Two', testimonial_text='Second review.')
        review3 = Review(author_name='Author Three', testimonial_text='Third review.')
        db.session.add_all([review1, review2, review3])
        db.session.commit()

        # Verify all three are on the list page by checking for their text
        list_response = client.get(url_for('review.index_view'))
        assert b'Author One' in list_response.data
        assert b'Author Two' in list_response.data
        assert b'Author Three' in list_response.data

        # Edit ONLY the second review
        client.post(
            url_for('review.edit_view', id=review2.id),
            data={'author_name': 'Author Two EDITED', 'testimonial_text': 'Second review EDITED.'},
            follow_redirects=True
        )

        db.session.refresh(review1)
        db.session.refresh(review2)
        db.session.refresh(review3)
        assert review1.author_name == 'Author One'
        assert review2.author_name == 'Author Two EDITED'
        assert review3.author_name == 'Author Three'

        # Delete ONLY the first review
        client.post(
            url_for('review.delete_view', id=review1.id),
            data={'id': review1.id}, # Send ID in form body
            follow_redirects=True
        )

        assert db.session.get(Review, review1.id) is None
        assert db.session.get(Review, review2.id) is not None
        assert db.session.get(Review, review3.id) is not None