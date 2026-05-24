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

def _fill_signup_form(driver):
    email = driver.find_element(By.CSS_SELECTOR, 'input[placeholder="example@email.com"]')
    name = driver.find_element(By.XPATH, "//label[contains(normalize-space(.), 'Full Name')]/following::input[1]")
    username = driver.find_element(By.XPATH, "//label[contains(normalize-space(.), 'Username')]/following::input[1]")
    phone = driver.find_element(By.XPATH, "//label[contains(normalize-space(.), 'Phone Number')]/following::input[1]")
    sel_el = driver.find_element(By.CSS_SELECTOR, '#company')
    select = Select(sel_el)
    for opt in select.options:
        val = opt.get_attribute('value') or ''
        if val.strip():
            opt.click()
            break

    password = driver.find_element(By.XPATH, "//label[contains(normalize-space(.), 'Password')]/following::input[1]")
    confirm = driver.find_element(By.XPATH, "//label[contains(normalize-space(.), 'Confirm Password')]/following::input[1]")

    email.clear(); email.send_keys('admin1@drone4dengue.com')
    name.clear(); name.send_keys('Tester Su')
    username.clear(); username.send_keys('testuser')
    phone.clear(); phone.send_keys('+60112345678')
    password.clear(); password.send_keys('testerHui3!')
    confirm.clear(); confirm.send_keys('testerHui3!')


def test_existing_email_rejected(driver):
    wait = WebDriverWait(driver, 30)

    driver.get(f"{BASE_URL}/signup")
    wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'input[placeholder="example@email.com"]')))

    accept_btn = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[aria-label="Accept Terms and Privacy Policy"]')))
    try:
        accept_btn.click()
    except Exception:
        driver.execute_script('arguments[0].click();', accept_btn)

    _fill_signup_form(driver)

    create_btn = driver.find_element(By.XPATH, "//*[contains(text(), 'SIGN UP')]")
    try:
        create_btn.click()
    except Exception:
        driver.execute_script('arguments[0].click();', create_btn)

    wait.until(
        EC.presence_of_element_located(
            (
                By.XPATH,
                "//*[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'already registered') or contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'email already')]",
            )
        )
    )

    page = driver.page_source.lower()
    assert 'already registered' in page or 'email already' in page
    assert 'registration successful!' not in page
