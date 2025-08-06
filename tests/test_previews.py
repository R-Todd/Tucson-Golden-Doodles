# tests/test_previews.py

from flask import url_for
from unittest.mock import patch
from app.models import User, HeroSection, SiteMeta, Parent, ParentRole
from bs4 import BeautifulSoup

def test_admin_hero_section_edit_page_has_live_preview(client, db):
    """
    GIVEN an authenticated admin user
    WHEN the Hero Section edit page is requested
    THEN check that the response contains the live preview HTML structure
    and the necessary IDs for JavaScript to function.
    """
    # --- Setup ---
    admin_user = User(username='admin'); admin_user.set_password('password123')
    hero = HeroSection(main_title='Initial Title')
    db.session.add_all([admin_user, hero, SiteMeta(email='contact@test.com')])
    db.session.commit()

    client.post(url_for('admin_auth.login'), data={'username': 'admin', 'password': 'password123'}, follow_redirects=True)
    
    # --- Action ---
    response = client.get(url_for('herosection.edit_view', id=hero.id))
    assert response.status_code == 200

    # --- Verification ---
    soup = BeautifulSoup(response.data, 'html.parser')
    
    preview_container = soup.find('div', class_='live-preview-container')
    assert preview_container is not None, "The live-preview-container div is missing."
    assert preview_container.find('h3').text == "Live Preview"

    preview_title = preview_container.find('h1', id='preview-main-title')
    assert preview_title is not None, "The preview title element with the correct ID is missing."
    
    preview_subtitle = preview_container.find('h2', id='preview-subtitle')
    assert preview_subtitle is not None, "The preview subtitle element with the correct ID is missing."

    form_title_input = soup.find('input', id='main_title')
    assert form_title_input is not None, "The main_title form input is missing its ID."
    
    form_subtitle_input = soup.find('input', id='subtitle')
    assert form_subtitle_input is not None, "The subtitle form input is missing its ID."


# --- NEW TEST WITH PRINT STATEMENTS ---
@patch('app.utils.template_filters.generate_presigned_url', return_value='http://mocked.com/image.jpg')
def test_admin_parent_edit_page_has_live_preview_with_debugging(mock_s3_url, client, db):
    """
    GIVEN an authenticated admin user and a parent object
    WHEN the Parent edit page is requested
    THEN check that the response contains the full live preview HTML structure
    with detailed print statements for debugging.
    """
    print("\n--- Running Parent Live Preview Test ---")
    
    # --- Setup ---
    admin_user = User(username='admin'); admin_user.set_password('password123')
    parent = Parent(name='Archie', role=ParentRole.DAD, breed='F1 Mini Poodle', weight_kg=8.5)
    db.session.add_all([admin_user, parent, SiteMeta(email='contact@test.com')])
    db.session.commit()

    client.post(url_for('admin_auth.login'), data={'username': 'admin', 'password': 'password123'}, follow_redirects=True)

    # --- Action ---
    print(f"Requesting page: {url_for('parent.edit_view', id=parent.id)}")
    response = client.get(url_for('parent.edit_view', id=parent.id))
    assert response.status_code == 200
    
    # --- Verification ---
    soup = BeautifulSoup(response.data, 'html.parser')

    # 1. Check for the main preview container
    preview_container = soup.find('div', class_='live-preview-container')
    print(f"\n1. Checking for 'div.live-preview-container': {'FOUND' if preview_container else 'MISSING'}")
    assert preview_container is not None

    # 2. Check for the Name Banner
    name_banner = preview_container.find('div', class_='parent-name-banner')
    print(f"2. Checking for 'div.parent-name-banner': {'FOUND' if name_banner else 'MISSING'}")
    assert name_banner is not None

    preview_name = name_banner.find('h1', id='preview-parent-name')
    print(f"   - Checking for 'h1#preview-parent-name': {'FOUND' if preview_name else 'MISSING'}")
    assert preview_name is not None

    # 3. Check for the Image Carousel Wrapper
    image_wrapper = preview_container.find('div', class_='parent-carousel-wrapper')
    print(f"3. Checking for 'div.parent-carousel-wrapper': {'FOUND' if image_wrapper else 'MISSING'}")
    assert image_wrapper is not None
    
    preview_image = image_wrapper.find('img', id='preview-parent-image')
    print(f"   - Checking for 'img#preview-parent-image': {'FOUND' if preview_image else 'MISSING'}")
    assert preview_image is not None

    # 4. Check for Info Column Elements
    info_column = preview_container.find('div', class_='parent-info-column')
    print(f"4. Checking for 'div.parent-info-column': {'FOUND' if info_column else 'MISSING'}")
    assert info_column is not None

    preview_breed = info_column.find('h3', id='preview-parent-breed')
    print(f"   - Checking for 'h3#preview-parent-breed': {'FOUND' if preview_breed else 'MISSING'}")
    assert preview_breed is not None

    preview_weight = info_column.find('p', id='preview-parent-weight')
    print(f"   - Checking for 'p#preview-parent-weight': {'FOUND' if preview_weight else 'MISSING'}")
    assert preview_weight is not None
    
    preview_description = info_column.find('div', id='preview-parent-description')
    print(f"   - Checking for 'div#preview-parent-description': {'FOUND' if preview_description else 'MISSING'}")
    assert preview_description is not None
    
    # 5. Check that FORM fields have the correct IDs for JS
    form_name = soup.find('input', id='name')
    form_breed = soup.find('input', id='breed')
    form_weight = soup.find('input', id='weight_kg')
    form_description = soup.find('textarea', id='description')
    
    print("\n5. Checking form input IDs:")
    print(f"   - 'input#name': {'FOUND' if form_name else 'MISSING'}")
    print(f"   - 'input#breed': {'FOUND' if form_breed else 'MISSING'}")
    print(f"   - 'input#weight_kg': {'FOUND' if form_weight else 'MISSING'}")
    print(f"   - 'textarea#description': {'FOUND' if form_description else 'MISSING'}")
    
    assert form_name and form_breed and form_weight and form_description, "One or more form input IDs are missing."

    print("\n--- Test Passed: All required elements for live preview are present. ---\n")