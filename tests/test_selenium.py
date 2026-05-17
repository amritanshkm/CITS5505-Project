import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import uuid

# NOTE: These tests expect the live server to be running on localhost:5000 
# during the execution, as per the rubric.
# Setup instructions: python run.py

@pytest.fixture(scope="module")
def driver():
    chrome_options = Options()
    # chrome_options.add_argument("--headless")  # Commented out so you can see the browser operate
    # In some local cases you might need to specify the executable path or remove headless to see it happen
    driver = webdriver.Chrome(options=chrome_options)
    yield driver
    driver.quit()

def test_home_page_title(driver):
    """Test 1: Check website title."""
    driver.get("http://127.0.0.1:5000/")
    assert "Event Finder" in driver.title

def test_login_empty_form_validation(driver):
    """Test 2: Check JS prevents empty form submission via showing red text."""
    driver.get("http://127.0.0.1:5000/login")
    driver.find_element(By.ID, "loginForm").submit()
    time.sleep(0.5)
    
    email_error = driver.find_element(By.ID, "emailError").text
    assert "Email is required" in email_error

def test_register_flow_e2e(driver):
    """Test 3: E2E test for successful registration."""
    driver.get("http://127.0.0.1:5000/register")
    unique_id = uuid.uuid4().hex[:8]
    unique_email = f"test_{unique_id}@test.com"
    unique_name = f"SeleniumUser_{unique_id}"
    
    driver.find_element(By.ID, "userName").send_keys(unique_name)
    driver.find_element(By.ID, "regEmail").send_keys(unique_email)
    driver.find_element(By.ID, "regPassword").send_keys("password123")
    driver.find_element(By.ID, "confirmPassword").send_keys("password123")
    
    driver.find_element(By.ID, "registerForm").submit()
    
    # Wait for redirect to login page and flash message
    WebDriverWait(driver, 5).until(EC.url_to_be("http://127.0.0.1:5000/login"))
    body_text = driver.find_element(By.TAG_NAME, "body").text
    assert "Registration successful!" in body_text

def test_login_flow_e2e(driver):
    """Test 4: E2E test for successful login using the previously registered user."""
    # First register a user identically
    unique_id = uuid.uuid4().hex[:8]
    unique_email = f"log_{unique_id}@test.com"
    unique_name = f"LoginTester_{unique_id}"
    
    driver.get("http://127.0.0.1:5000/register")
    driver.find_element(By.ID, "userName").send_keys(unique_name)
    driver.find_element(By.ID, "regEmail").send_keys(unique_email)
    driver.find_element(By.ID, "regPassword").send_keys("password123")
    driver.find_element(By.ID, "confirmPassword").send_keys("password123")
    driver.find_element(By.ID, "registerForm").submit()
    WebDriverWait(driver, 5).until(EC.url_to_be("http://127.0.0.1:5000/login"))
    
    # Now login with it
    driver.get("http://127.0.0.1:5000/login")
    driver.find_element(By.ID, "email").send_keys(unique_email)
    driver.find_element(By.ID, "password").send_keys("password123")
    driver.find_element(By.ID, "loginForm").submit()
    
    # Wait for redirect to index
    WebDriverWait(driver, 5).until(EC.url_contains("/events"))
    body_text = driver.find_element(By.TAG_NAME, "body").text
    assert "Login successful!" in body_text
    
    # Test Dynamic Navbar checking if "My Profile" exists after login
    assert "My Profile" in driver.page_source

def test_protected_route_rejection(driver):
    """Test 5: E2E test verifying @login_required decorator blocks anonymous users."""
    driver.get("http://127.0.0.1:5000/logout") # Ensure logged out
    time.sleep(0.5)
    
    # Try accessing profile
    driver.get("http://127.0.0.1:5000/profile")
    
    # Should redirect to login
    WebDriverWait(driver, 5).until(EC.url_contains("/login"))
    body_text = driver.find_element(By.TAG_NAME, "body").text
    assert "Please log in to access this page." in body_text
