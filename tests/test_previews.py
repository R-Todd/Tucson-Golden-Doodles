# tests/test_previews.py

from flask import url_for
from app.models import User, HeroSection, SiteDetails
from bs4 import BeautifulSoup

def test_admin_hero_section_edit_page_has_live_preview(client, db):
    """
    GIVEN an authenticated admin user
    WHEN the Hero Section edit page is requested
    THEN check that the response contains the live preview HTML structure
    and the necessary IDs for JavaScript to function.
    """
    # --- Setup ---
    # Create a dummy admin user and log them in
    admin_user = User(username='admin')
    admin_user.set_password('password123')
    # A HeroSection and SiteDetails are needed for the page to render
    hero = HeroSection(main_title='Initial Title')
    db.session.add_all([admin_user, hero, SiteDetails(email='contact@test.com')])
    db.session.commit()

    # Log in the user
    client.post(
        url_for('admin_auth.login'),
        data={'username': 'admin', 'password': 'password123'},
        follow_redirects=True
    )

    # --- Action ---
    # Request the edit page for the HeroSection
    response = client.get(url_for('herosection.edit_view', id=hero.id))
    assert response.status_code == 200

    # --- Verification ---
    # Parse the HTML to verify its contents
    soup = BeautifulSoup(response.data, 'html.parser')

    # 1. Check if the main preview container exists
    preview_container = soup.find('div', class_='live-preview-container')
    assert preview_container is not None, "The live-preview-container div is missing."
    assert preview_container.find('h3').text == "Live Preview"

    # 2. Check for specific preview elements with correct IDs
    preview_title = preview_container.find('h1', id='preview-main-title')
    assert preview_title is not None, "The preview title element with the correct ID is missing."
    
    preview_subtitle = preview_container.find('h2', id='preview-subtitle')
    assert preview_subtitle is not None, "The preview subtitle element with the correct ID is missing."

    # 3. Check that the FORM input fields have the correct IDs for the JS to find
    form_title_input = soup.find('input', id='main_title')
    assert form_title_input is not None, "The main_title form input is missing its ID."
    assert form_title_input['name'] == 'main_title'
    
    form_subtitle_input = soup.find('input', id='subtitle')
    assert form_subtitle_input is not None, "The subtitle form input is missing its ID."
    assert form_subtitle_input['name'] == 'subtitle'