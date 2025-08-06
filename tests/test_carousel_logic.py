# tests/test_carousel_logic.py

import pytest
import time
from flask import url_for
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from app.models import User, Parent, ParentRole, SiteMeta

# --- THIS IS THE FIX ---
# We've added `db` to the function signature to ensure
# the database creation fixture runs before this one.
@pytest.fixture(scope='module')
def setup_parent_data(app, db):
    """Set up a user and parent for the selenium tests."""
    with app.app_context():
        # Clean up previous data to ensure a fresh start
        db.session.query(User).delete()
        db.session.query(Parent).delete()
        db.session.query(SiteMeta).delete()

        admin_user = User(username='admin_sel')
        admin_user.set_password('selenium_pw')
        parent = Parent(
            name='Archie', role=ParentRole.DAD,
            main_image_s3_key='parents/archie.jpg',
            alternate_image_s3_key_1='parents/archie-2.jpg'
        )
        db.session.add_all([admin_user, parent, SiteMeta(email='test@test.com')])
        db.session.commit()
        return admin_user, parent

def test_live_preview_carousel_functionality(chrome_driver, live_server, setup_parent_data):
    """
    GIVEN a running Flask application with a parent object.
    WHEN an admin logs in and views the parent edit page.
    THEN the live preview carousel should auto-cycle, and manual controls
    should correctly switch slides and stop the auto-cycling.
    """
    admin_user, parent = setup_parent_data
    driver = chrome_driver

    # 1. Log in to the admin panel
    driver.get(f"{live_server.url}{url_for('admin_auth.login')}")
    driver.find_element(By.ID, 'username').send_keys(admin_user.username)
    driver.find_element(By.ID, 'password').send_keys('selenium_pw')
    driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]').click()

    # 2. Navigate to the Parent Edit Page
    driver.get(f"{live_server.url}{url_for('parent.edit_view', id=parent.id)}")

    # 3. Verify the carousel and initial state
    wait = WebDriverWait(driver, 10)
    carousel = wait.until(EC.presence_of_element_located((By.ID, 'live-preview-carousel')))
    
    first_image = carousel.find_element(By.ID, 'preview-parent-image')
    second_image = carousel.find_element(By.ID, 'preview-alt-image-1')

    # Confirm the first image is active initially
    active_item = carousel.find_element(By.CSS_SELECTOR, '.carousel-item.active')
    assert first_image in active_item.find_elements(By.TAG_NAME, 'img'), "Initial active image is not the main one."
    print("\n✅ Test Passed: Carousel is present and initial image is correct.")

    # 4. Verify auto-cycling
    time.sleep(6) # The interval is 5s, so we wait slightly longer
    
    active_item_after_cycle = carousel.find_element(By.CSS_SELECTOR, '.carousel-item.active')
    assert second_image in active_item_after_cycle.find_elements(By.TAG_NAME, 'img'), "Carousel did not auto-cycle to the second image."
    print("✅ Test Passed: Carousel auto-cycled successfully.")

    # 5. Click the 'next' button and verify slide change
    next_button = carousel.find_element(By.CSS_SELECTOR, '.carousel-control-next')
    next_button.click()
    
    time.sleep(1) # Wait for the slide transition to complete

    active_item_after_click = carousel.find_element(By.CSS_SELECTOR, '.carousel-item.active')
    # Since it already cycled to the 2nd image and there are only two images,
    # clicking next should wrap around back to the 1st image.
    assert first_image in active_item_after_click.find_elements(By.TAG_NAME, 'img'), "Next button did not cycle the image correctly."
    print("✅ Test Passed: 'Next' button successfully changed the slide.")

    # 6. Verify that auto-cycling has STOPPED after manual interaction
    current_active_image_src = active_item_after_click.find_element(By.TAG_NAME, 'img').get_attribute('src')
    
    time.sleep(6) # Wait for another cycle period
    
    final_active_item = carousel.find_element(By.CSS_SELECTOR, '.carousel-item.active')
    final_active_image_src = final_active_item.find_element(By.TAG_NAME, 'img').get_attribute('src')
    
    assert current_active_image_src == final_active_image_src, "Carousel continued to auto-cycle after manual interaction."
    print("✅ Test Passed: Carousel correctly stopped auto-cycling after a manual click.")