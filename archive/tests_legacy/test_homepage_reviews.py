# tests/test_homepage_reviews.py

import pytest
from flask import url_for
from app.models import Review, db

def test_featured_review_appears_on_homepage(client, db):
    """
    GIVEN a review that is marked as featured
    WHEN the homepage is loaded
    THEN the review's text and author should be visible.
    """
    # Create one featured and one non-featured review
    featured_review = Review(
        author_name="The Happy Family",
        testimonial_text="This puppy is wonderful!",
        is_featured=True
    )
    non_featured_review = Review(
        author_name="The Other Family",
        testimonial_text="We also love our puppy.",
        is_featured=False
    )
    db.session.add_all([featured_review, non_featured_review])
    db.session.commit()

    # Request the homepage
    response = client.get(url_for('main.index'))
    assert response.status_code == 200

    # Check that the FEATURED review's content is present
    assert b"This puppy is wonderful!" in response.data
    assert b"The Happy Family" in response.data

    # Check that the NON-FEATURED review's content is NOT present
    assert b"We also love our puppy." not in response.data