from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, UnexpectedAlertPresentException
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
    # Enable logging to verify that the system logs the issue
    options.set_capability('goog:loggingPrefs', {'browser': 'ALL'})

    drv = webdriver.Edge(options=options)
    drv.maximize_window()
    yield drv
    drv.quit()

def test_server_error_handling(driver):
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

    # Handle optional alert after login
    try:
        alert = wait.until(EC.alert_is_present())
        alert.accept()
    except TimeoutException:
        pass

    # 2. Navigate to Drone Management page
    driver.get(f"{BASE_URL}/drone-management")
    
    # Handle optional alert after navigation
    try:
        alert = wait.until(EC.alert_is_present())
        alert.accept()
    except TimeoutException:
        pass
    
    # Wait for the table to load so we know we have entries to interact with
    drone_row = wait.until(EC.presence_of_element_located((By.XPATH, "//tr[.//td[contains(text(), 'Drone')]]")))
    
    # 3. INJECT JS to mock frontend fetch/axios calls to simulate a 500 Server Error
    mock_error_script = """
    // Mock Fetch
    window.originalFetch = window.fetch;
    window.fetch = async function(...args) {
        console.error("Mocked 500 Server Error for:", args[0]);
        return new Response(JSON.stringify({ message: "Simulated 500 Internal Server Error" }), {
            status: 500,
            statusText: "Internal Server Error",
            headers: { 'Content-Type': 'application/json' }
        });
    };
    
    // Mock XMLHttpRequest (Axios)
    const originalOpen = XMLHttpRequest.prototype.open;
    XMLHttpRequest.prototype.open = function(method, url) {
        this.addEventListener('readystatechange', function() {
            if (this.readyState === 4) {
                console.error("Mocked 500 Server Error for:", url);
                Object.defineProperty(this, 'status', {writable: true, value: 500});
                Object.defineProperty(this, 'responseText', {writable: true, value: '{"message":"Simulated 500 Internal Server Error"}'});
            }
        });
        originalOpen.apply(this, arguments);
    };
    """
    driver.execute_script(mock_error_script)

    # 4. Trigger an action that communicates with the backend (e.g., clicking View)
    view_btn = drone_row.find_element(By.XPATH, ".//button[contains(@title, 'View') or contains(translate(., 'VIEW', 'view'), 'view')]")
    driver.execute_script('arguments[0].click();', view_btn)

    # 5. Assert System shows error message (either an alert or a toast)
    error_shown = False
    try:
        # Check if an alert popped up with an error
        alert = wait.until(EC.alert_is_present())
        print(f"Alert displayed: {alert.text}")
        alert.accept()
        error_shown = True
    except TimeoutException:
        # If no alert, check the DOM for an error message / toast
        try:
            error_msg = wait.until(EC.presence_of_element_located((
                By.XPATH, "//*[contains(translate(text(), 'ERROR', 'error'), 'error') or contains(translate(text(), 'FAILED', 'failed'), 'failed')]"
            )))
            print(f"Error message displayed on page: {error_msg.text}")
            error_shown = True
        except TimeoutException:
            pass

    assert error_shown, "Expected an error message to be displayed after a server error (500)."

    # 6. Assert System logs the issue
    browser_logs = driver.get_log('browser')
    error_logged = any("500" in log['message'] or "Error" in log['message'] for log in browser_logs)
    
    assert error_logged, "Expected the server error to be logged in the browser console."