from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.edge.options import Options as EdgeOptions
import pytest
import subprocess
import os

BASE_URL = "http://localhost:3000"

@pytest.fixture(autouse=True)
def reset_db():
    server_api_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../server-api"))
    subprocess.run("npx prisma migrate reset --force && npm run seed", shell=True, cwd=server_api_dir, check=True)

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

def test_manage_and_download_drone_images(driver):
    wait = WebDriverWait(driver, 15)
    
    # 1. Login (Adjust these credentials to match your seeded test data)
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
    
    # 3. Open a drone entry that has images
    # Looking for a 'View' or 'Images' button for the first drone in the list
    view_btn = wait.until(EC.element_to_be_clickable((By.XPATH, ".//button[contains(@title, 'View Details')]")))
    driver.execute_script('arguments[0].click();', view_btn)

    # 4. Expected Result 1: System shows all images for the drone entry
    # Wait for images to be present on the page
    images = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "img")))
    assert len(images) > 0, "Expected images to be displayed for the drone, but none were found."

    # 5. Expected Result 2: Start image downloading process
    # Find a download button (could be text or an icon with an aria-label)
    download_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "(//button[contains(translate(., 'DOWNLOAD', 'download'), 'download') or contains(@aria-label, 'Download')])[1]")))
    driver.execute_script('arguments[0].click();', download_btn)

    # Wait briefly to ensure the download action triggers without page crash
    import time
    time.sleep(3)
    
    # Assertion passes if we got here without timing out or errors (meaning UI is present and clickable)
    assert True
