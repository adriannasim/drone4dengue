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

@pytest.mark.parametrize(
    "email, full_name, username, phone, choose_company, password, confirm_password, check_terms",
    [
        # 1. All blank, company not selected, unchecked
        ("", "", "", "", False, "", "", False),
        # 2. Full Name blank
        ("test@gmail.com", "", "testuser", "60112345678", True, "testerHui3!", "testerHui3!", True),
        # 3. Email blank
        ("", "Tester Su", "testuser", "60112345678", True, "testerHui3!", "testerHui3!", True),
        # 4. Password blank
        ("test@gmail.com", "Tester Su", "testuser", "60112345678", True, "", "testerHui3!", True),
        # 5. Phone blank
        ("test@gmail.com", "Tester Su", "testuser", "", True, "testerHui3!", "testerHui3!", True),
    ]
)
def test_invalid_registration_missing_fields(driver, email, full_name, username, phone, choose_company, password, confirm_password, check_terms):
    wait = WebDriverWait(driver, 30)
    driver.get(f"{BASE_URL}/signup")

    # wait for form
    wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'input[placeholder="example@email.com"]')))

    email_input = driver.find_element(By.CSS_SELECTOR, 'input[placeholder="example@email.com"]')
    name_input = driver.find_element(By.XPATH, "//label[contains(normalize-space(.), 'Full Name')]/following::input[1]")
    username_input = driver.find_element(By.XPATH, "//label[contains(normalize-space(.), 'Username')]/following::input[1]")
    phone_input = driver.find_element(By.XPATH, "//label[contains(normalize-space(.), 'Phone Number')]/following::input[1]")

    # company select
    if choose_company:
        sel_el = driver.find_element(By.CSS_SELECTOR, '#company')
        select = Select(sel_el)
        for opt in select.options:
            val = opt.get_attribute('value') or ''
            if val.strip():
                opt.click()
                break

    password_input = driver.find_element(By.XPATH, "//label[contains(normalize-space(.), 'Password')]/following::input[1]")
    confirm_input = driver.find_element(By.XPATH, "//label[contains(normalize-space(.), 'Confirm Password')]/following::input[1]")

    # accept terms
    if check_terms:
        accept_btn = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[aria-label="Accept Terms and Privacy Policy"]')))
        try:
            accept_btn.click()
        except Exception:
            driver.execute_script('arguments[0].click();', accept_btn)

    # fill fields
    email_input.clear(); email_input.send_keys(email)
    name_input.clear(); name_input.send_keys(full_name)
    username_input.clear(); username_input.send_keys(username)
    phone_input.clear(); phone_input.send_keys(phone)
    password_input.clear(); password_input.send_keys(password)
    confirm_input.clear(); confirm_input.send_keys(confirm_password)

    # submit
    create_btn = driver.find_element(By.XPATH, "//*[contains(text(), 'SIGN UP')]")
    try:
        create_btn.click()
    except Exception:
        driver.execute_script('arguments[0].click();', create_btn)

    # Fast short check if any HTML5 validation messages pop up (they trigger if 'required' inputs are blank)
    try:
        wait_short = WebDriverWait(driver, 2)
        # Because we don't know exactly which field triggers the tooltip first, we check if the URL didn't change quickly
        wait_short.until(lambda d: d.current_url.rstrip('/') == f"{BASE_URL}/signup".rstrip('/'))
    except TimeoutException:
        pass # Moving on to the main check below
        
    # Check if submission succeeded (fail the test if it did, since we expect it to be rejected)
    try:
        wait_success = WebDriverWait(driver, 5)
        # If the URL changes away from signup, it successfully registered (or crashed), which is a FAIL for missing fields
        wait_success.until(lambda d: d.current_url.rstrip('/') != f"{BASE_URL}/signup".rstrip('/'))
        pytest.fail('Form succeeded unexpectedly for invalid/blank fields')
    except TimeoutException:
        # Stayed on sign up (pass)
        assert driver.current_url.rstrip('/') == f"{BASE_URL}/signup".rstrip('/')
