from app.models import Parent, ParentRole, HeroSection, AboutSection, Puppy, PuppyStatus, Review
from datetime import date

def test_homepage_route(client, db):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/' route is requested (GET)
    THEN check that the response is valid and contains expected content
    """
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
    THEN check that the response is valid and displays parent names and litter info
    """
    # Seed the database with parents, including a description to prevent Jinja2 error
    parent1 = Parent(name='Archie', role=ParentRole.DAD, main_image_url='img/archie.jpg', description='A test dad description.')
    parent2 = Parent(name='Luna', role=ParentRole.MOM, main_image_url='img/luna.jpg', description='A test mom description.')
    db.session.add(parent1)
    db.session.add(parent2)
    db.session.commit() # Commit to get IDs

    # Add a puppy to test the "Past Litters" section
    puppy = Puppy(name='Test Puppy', mom_id=parent2.id, dad_id=parent1.id, birth_date=date(2023, 1, 1), main_image_url='img/puppy.jpg')
    db.session.add(puppy)
    db.session.commit()

    response = client.get('/parents')
    assert response.status_code == 200
    # Fix: Assert parent names from the new dynamic banners (uppercase as per template)
    assert b"ARCHIE" in response.data
    assert b"LUNA" in response.data
    # Fix: Assert the updated "Past Puppies" section header
    assert b"PAST PUPPIES" in response.data # Part of "ARCHIE'S PAST PUPPIES"

def test_homepage_empty_state(client, db):
    """
    GIVEN a Flask application with an empty database
    WHEN the '/' route is requested (GET)
    THEN check that placeholder messages are shown
    """
    response = client.get('/')
    assert response.status_code == 200
    assert b"We don't have any available puppies at the moment" in response.data
    assert b"What Our Families Say" not in response.data

def test_homepage_guardian_parents_section(client, db):
    """
    GIVEN a Flask application
    WHEN the homepage is requested and there are guardian parents
    THEN check that only guardian parents are displayed in the correct section
    """
    # Create one guardian parent and one regular parent
    guardian_parent = Parent(name='GuardianDog', role=ParentRole.MOM, is_guardian=True, description='A guardian parent')
    regular_parent = Parent(name='RegularDog', role=ParentRole.DAD, is_guardian=False, description='A regular parent')
    db.session.add_all([guardian_parent, regular_parent])
    db.session.commit()

    response = client.get('/')
    assert response.status_code == 200
    
    # Check that the "Guardian Parents" title and the guardian dog's name are present
    assert b'Guardian Parents' in response.data
    assert b'GuardianDog' in response.data
    
    # Check that the regular (non-guardian) dog's name is not present
    assert b'RegularDog' not in response.data