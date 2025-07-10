from app.models import Parent, ParentRole, HeroSection, AboutSection, Puppy, PuppyStatus, Review
from datetime import date

def test_homepage_route(client, db):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/' route is requested (GET)
    THEN check that the response is valid and contains expected content
    """
    # Seed the database with some content for the homepage
    hero = HeroSection(title='Test Hero Title', subtitle='Test Subtitle', image_url='img/test.jpg')
    about = AboutSection(title='About Us Test', content_html='<p>Test Content</p>', image_url='img/test.jpg')
    db.session.add_all([hero, about])
    db.session.commit()

    response = client.get('/')
    assert response.status_code == 200
    assert b"Tucson Golden Doodles" in response.data
    assert b"Test Hero Title" in response.data
    assert b"About Us Test" in response.data
    assert b"Test Content" in response.data

def test_parents_page_route(client, db):
    """
    GIVEN a Flask application
    WHEN the '/parents' route is requested (GET)
    THEN check that the response is valid and displays parent names
    """
    # Seed the database with parents
    parent1 = Parent(name='Archie', role=ParentRole.DAD, main_image_url='img/archie.jpg')
    parent2 = Parent(name='Luna', role=ParentRole.MOM, main_image_url='img/luna.jpg')
    db.session.add(parent1)
    db.session.add(parent2)
    db.session.commit() # Commit to get IDs

    # Add a puppy to test the "Past Litters" section
    puppy = Puppy(name='Test Puppy', mom_id=parent2.id, dad_id=parent1.id, birth_date=date(2023, 1, 1), main_image_url='img/puppy.jpg')
    db.session.add(puppy)
    db.session.commit()

    response = client.get('/parents')
    assert response.status_code == 200
    assert b"Our Wonderful Parents" in response.data
    assert b"Archie" in response.data
    assert b"Luna" in response.data
    assert b"Past Litters" in response.data # Check that the section appears
    # Check for the components separately to avoid whitespace sensitivity
    assert b"Litter with" in response.data
    assert b"<strong>Archie</strong>" in response.data

def test_homepage_empty_state(client, db):
    """
    GIVEN a Flask application with an empty database
    WHEN the '/' route is requested (GET)
    THEN check that placeholder messages are shown
    """
    # The 'db' fixture ensures tables are created but are empty.
    response = client.get('/')
    assert response.status_code == 200
    # Check for the message that appears when there are no available puppies
    assert b"We don't have any available puppies at the moment" in response.data
    # Check that the testimonials section does not render if there are none
    assert b"What Our Families Say" not in response.data