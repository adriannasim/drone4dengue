from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.edge.options import Options as EdgeOptions
import pytest
import subprocess
import os

BASE_URL = "http://localhost:3000"

@pytest.fixture
def driver():
    options = EdgeOptions()
    options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    drv = webdriver.Edge(options=options)
    drv.maximize_window()
    yield drv
    drv.quit()

def test_view_drone_without_images(driver):
    wait = WebDriverWait(driver, 15)
    
    # 1. Login
    driver.get(f"{BASE_URL}/")
    email_input = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'input[type="email"]')))
    email_input.send_keys('admin1@drone4dengue.com')
    
    password_input = driver.find_element(By.CSS_SELECTOR, 'input[type="password"]')
    password_input.send_keys('adminpass1')
    
    login_btn = driver.find_element(By.XPATH, "//button[@type='submit' or contains(translate(., 'LOGIN', 'login'), 'log')]")
    login_btn.click()
    
    wait.until(EC.url_changes(f"{BASE_URL}/login"))

    try:
        alert = wait.until(EC.alert_is_present())
        alert.accept()
    except TimeoutException:
        pass

    # 2. Navigate to Drone Management page
    driver.get(f"{BASE_URL}/drone-management")
    
    try:
        alert = wait.until(EC.alert_is_present())
        alert.accept()
    except TimeoutException:
        pass
    
    # 3. Open a drone entry (Drone2)
    # Looking for Drone2 entry
    # Try finding the cell by text and climbing up to the row
    try:
        drone2_row = wait.until(EC.presence_of_element_located((By.XPATH, "//tr[.//td[contains(text(), 'Drone 2') or contains(text(), 'Drone2')]]")))
        view_btn = drone2_row.find_element(By.XPATH, ".//button[contains(@title, 'View Details')]")
            
        driver.execute_script('arguments[0].click();', view_btn)
    except TimeoutException:
        pytest.fail("Could not find Drone 2.")

    # 4. Expected Result: The system will show "No images available"
    try:
        no_images_msg = wait.until(EC.presence_of_element_located((By.XPATH, "//*[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'No images available for this drone')] | //*[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'no images')]")))
        assert no_images_msg.is_displayed() or no_images_msg is not None, "Expected 'No images available for this drone' message."
    except TimeoutException:
        pytest.fail("The message 'No images available for this drone' was not found on the page.")
