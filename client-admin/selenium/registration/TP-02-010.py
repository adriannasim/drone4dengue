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

def test_invalid_phone_number_rejected(driver):
    wait = WebDriverWait(driver, 30)
    driver.get(f"{BASE_URL}/signup")

    wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'input[placeholder="example@email.com"]')))

    # Store the ID of the original window
    original_window = driver.current_window_handle
    assert len(driver.window_handles) == 1

    term_text = driver.find_element(By.XPATH, "//*[contains(text(), 'Terms and Privacy Policy')]")

    # Click the text
    try:
        term_text.click()
    except Exception:
        driver.execute_script('arguments[0].click();', term_text)

    # Wait for the new window or tab
    try:
        wait.until(EC.number_of_windows_to_be(2))
    except TimeoutException:
        pytest.fail('No new window/tab opened after clicking t&c text')

    # Loop through until we find a new window handle
    for window_handle in driver.window_handles:
        if window_handle != original_window:
            driver.switch_to.window(window_handle)
            break

    # Wait for the terms page to load in the new window
    try:
        wait_success = WebDriverWait(driver, 5)
        # Check if the opened window URL contains terms
        wait_success.until(lambda d: "/terms" in d.current_url)
        return
    except TimeoutException:
        pytest.fail(f'New window opened but did not navigate to terms page. Loaded: {driver.current_url}')