# tests/test_routes.py
from app.models import Parent, ParentRole, HeroSection, Puppy, PuppyStatus
from datetime import date
from unittest.mock import patch

@patch('app.utils.template_filters.generate_presigned_url', return_value='https://mocked-presigned-url.com/image.jpg')
def test_homepage_route_with_presigned_urls(mock_generate_url, client, db):
    """
    GIVEN an application with the new S3 key structure
    WHEN the '/' route is requested
    THEN check that the response contains the mocked pre-signed URL
    """
    hero = HeroSection(
        main_title='Test Hero Title',
        image_s3_key='hero/hero-image.jpg',
        image_s3_key_large='hero/hero-image-large.jpg'
    )
    db.session.add(hero)
    db.session.commit()

    response = client.get('/')
    assert response.status_code == 200
    assert b'https://mocked-presigned-url.com/image.jpg' in response.data
    assert b'hero/hero-image.jpg' not in response.data
    mock_generate_url.assert_called()


@patch('app.utils.template_filters.generate_presigned_url', return_value='https://mocked-parent-url.com/parent.jpg')
def test_parents_page_route_with_presigned_urls(mock_generate_url, client, db):
    """
    GIVEN an application with parents having S3 keys
    WHEN the '/parents' route is requested
    THEN check that the response contains mocked pre-signed URLs for parent images
    """
    parent = Parent(
        name='Archie',
        role=ParentRole.DAD,
        main_image_s3_key='parents/archie.jpg',
        description='A test dad.'
    )
    db.session.add(parent)
    db.session.commit()

    response = client.get('/parents')
    assert response.status_code == 200
    assert b'https://mocked-parent-url.com/parent.jpg' in response.data
    #
    # The name is rendered as 'Archie', and the `text-uppercase` class handles the styling.
    # The test should check for the actual data in the response.
    assert b'Archie' in response.data
    mock_generate_url.assert_called()