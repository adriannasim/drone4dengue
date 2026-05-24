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

    login_text = driver.find_element(By.XPATH, "//*[contains(text(), 'Login')]")

    # Click the text
    try:
        login_text.click()
    except Exception:
        driver.execute_script('arguments[0].click();', login_text)

    try:
        wait_success = WebDriverWait(driver, 5)
        wait_success.until(
            lambda d: d.current_url == f"{BASE_URL}/"
        )
        return
    except TimeoutException:
        # No redirect to login page, test fails
        assert driver.current_url == f"{BASE_URL}/signup"
        pytest.fail('No redirect to login page after clicking login text')
