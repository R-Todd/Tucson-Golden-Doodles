# tests/test_reviews_bs5.py

from flask import url_for
from bs4 import BeautifulSoup
from app.models import User, Review, SiteMeta, db


class TestReviewsAdminBS5:
    """
    Test suite for the Bootstrap 5 implementation of the Reviews admin section.
    """
    def _login(self, client, db, username='admin', password='password'):
        """Helper function to log in an admin user."""
        admin_user = User(username=username)
        admin_user.set_password(password)
        db.session.add(admin_user)
        db.session.add(SiteMeta(email='contact@test.com'))
        db.session.commit()
        
        return client.post(
            url_for('admin_auth.login'),
            data={'username': username, 'password': password},
            follow_redirects=True
        )

    def test_review_list_page_loads_with_bs5_and_actions(self, client, db):
        """
        GIVEN an authenticated admin user
        WHEN the /admin/review/ page is requested
        THEN check that the page loads with Bootstrap 5 and has 'Edit'/'Delete' buttons.
        """
        self._login(client, db)
        db.session.add(Review(author_name='Test Author', testimonial_text='A great review.'))
        db.session.commit()

        response = client.get(url_for('review.index_view'))
        assert response.status_code == 200

        soup = BeautifulSoup(response.data, 'html.parser')
        
        bs5_css = soup.find('link', href=lambda x: x and 'bootstrap@5' in x)
        assert bs5_css is not None, "Bootstrap 5 CSS is not loaded on the review list page."

        edit_action = soup.find('a', href=lambda x: x and 'review/edit' in x)
        assert edit_action is not None, "The 'Edit' button is missing from the review list."
        
        # --- THIS IS THE FIX ---
        # Instead of checking the button's visible text, we check its 'title' attribute.
        assert 'Edit Record' in edit_action['title'], "The 'Edit' button has an incorrect title attribute."

        delete_action_form = soup.find('form', action=lambda x: x and 'review/delete' in x)
        assert delete_action_form is not None, "The 'Delete' action form is missing."

    def test_create_review_saves_to_db(self, client, db):
        """
        GIVEN an authenticated admin user
        WHEN a new review is submitted via the create form
        THEN check that the new review is saved correctly in the database.
        """
        self._login(client, db)
        
        response = client.post(
            url_for('review.create_view'),
            data={
                'author_name': 'New Reviewer',
                'testimonial_text': 'This is a brand new testimonial.',
                'is_featured': 'y'
            },
            follow_redirects=True
        )

        assert response.status_code == 200
        assert b'Record was successfully created.' in response.data

        review = Review.query.filter_by(author_name='New Reviewer').first()
        assert review is not None
        assert review.testimonial_text == 'This is a brand new testimonial.'
        assert review.is_featured is True

    def test_edit_review_saves_changes_to_db(self, client, db):
        """
        GIVEN an authenticated admin user and an existing review
        WHEN the review is edited and saved
        THEN check that the changes are correctly persisted to the database.
        """
        self._login(client, db)
        review = Review(author_name='Old Author', testimonial_text='Old text.', is_featured=False)
        db.session.add(review)
        db.session.commit()

        response = client.post(
            url_for('review.edit_view', id=review.id),
            data={
                'author_name': 'Updated Author',
                'testimonial_text': 'This text has been updated.',
                'is_featured': 'y'
            },
            follow_redirects=True
        )

        assert response.status_code == 200
        assert b'Record was successfully saved.' in response.data

        db.session.refresh(review)
        assert review.author_name == 'Updated Author'
        assert review.testimonial_text == 'This text has been updated.'
        assert review.is_featured is True

    def test_delete_review_removes_from_db(self, client, db):
        """
        GIVEN an authenticated admin user and an existing review
        WHEN the review is deleted
        THEN check that it is removed from the database.
        """
        self._login(client, db)
        review_to_delete = Review(author_name='Delete Me', testimonial_text='I am about to be deleted.')
        db.session.add(review_to_delete)
        db.session.commit()
        review_id = review_to_delete.id

        response = client.post(
            url_for('review.delete_view', id=review_id),
            follow_redirects=True
        )
        
        assert response.status_code == 200
        assert b'Record was successfully deleted.' in response.data

        deleted_review = db.session.get(Review, review_id)
        assert deleted_review is None