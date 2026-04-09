import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
import time

# NOTE: These tests expect the live server to be running on localhost:5000 
# during the execution, as per the rubric.
# Setup instructions: python run.py

@pytest.fixture(scope="module")
def driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run headless for CI
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

def test_login_invalid_email_format(driver):
    """Test 3: Check JS catches invalid email format."""
    driver.get("http://127.0.0.1:5000/login")
    email_input = driver.find_element(By.ID, "email")
    email_input.send_keys("not-an-email")
    driver.find_element(By.ID, "loginForm").submit()
    time.sleep(0.5)
    
    email_error = driver.find_element(By.ID, "emailError").text
    assert "Please enter a valid email address" in email_error

def test_register_password_length_validation(driver):
    """Test 4: Check JS enforces minimum password length of 8."""
    driver.get("http://127.0.0.1:5000/register")
    password_input = driver.find_element(By.ID, "regPassword")
    password_input.send_keys("123")
    driver.find_element(By.ID, "registerForm").submit()
    time.sleep(0.5)
    
    password_error = driver.find_element(By.ID, "regPasswordError").text
    assert "at least 8 characters long" in password_error

def test_register_password_match_validation(driver):
    """Test 5: Check JS validates password match."""
    driver.get("http://127.0.0.1:5000/register")
    
    driver.find_element(By.ID, "regPassword").send_keys("password123")
    driver.find_element(By.ID, "confirmPassword").send_keys("differentpass")
    
    driver.find_element(By.ID, "registerForm").submit()
    time.sleep(0.5)
    
    match_error = driver.find_element(By.ID, "confirmPasswordError").text
    assert "Passwords do not match" in match_error
