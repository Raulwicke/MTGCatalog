from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException, TimeoutException
import time

# WebDriver Setup
def setup_driver():
    service = Service('C:/WebDriver/chromedriver.exe')  # Update this to your path
    options = webdriver.ChromeOptions()
    driver = webdriver.Chrome(service=service, options=options)
    return driver

# Logger for tracking issues
def log_issue(issue_type, description):
    print(f"[{issue_type}] {description}")

# Test Navigation
def test_navigation():
    driver = setup_driver()
    base_url = "http://127.0.0.1:5000"
    issues = []

    try:
        # Open Home Page
        driver.get(base_url)
        if "Catalog" not in driver.title:
            log_issue("Page Load Error", "Home page did not load correctly")
        
        # Try navigating to Login Page
        try:
            login_link = driver.find_element(By.LINK_TEXT, "Login")
            login_link.click()
            time.sleep(2)  # Wait for page to load
            if "Login" not in driver.title:
                log_issue("Navigation Error", "Failed to navigate to Login page")
        except NoSuchElementException:
            log_issue("Element Not Found", "Login link is missing on the home page")
        
        # Perform Login
        try:
            username_field = driver.find_element(By.NAME, "username")
            password_field = driver.find_element(By.NAME, "password")
            username_field.send_keys("Raulwicke")  # Replace with a valid username
            password_field.send_keys("3WtCtW\"ism\"")  # Replace with a valid password
            password_field.send_keys(Keys.RETURN)
            time.sleep(2)

            if "Catalog" not in driver.title:  # Assuming successful login redirects here
                log_issue("Login Error", "Login did not redirect to the expected page")
        except NoSuchElementException:
            log_issue("Element Not Found", "Username or Password field not found on Login page")

        # Test Navigation to Update Planeswalker
        try:
            update_link = driver.find_element(By.LINK_TEXT, "Update Planeswalker")
            update_link.click()
            time.sleep(2)
            try:
                username_field = driver.find_element(By.NAME, "username")
                password_field = driver.find_element(By.NAME, "password")
                username_field.send_keys("Raulwicke")  # Replace with a valid username
                password_field.send_keys("3WtCtW\"ism\"")  # Replace with a valid password
                password_field.send_keys(Keys.RETURN)
                time.sleep(2)

                if "Update Planeswalker" not in driver.title:  # Assuming successful login redirects here
                    log_issue("Navigation Error", "Failed to Login to Planeswalker page")
            except NoSuchElementException:
                log_issue("Element Not Found", "Username or Password field not found on Login page")
                if "Update Planeswalker" not in driver.title:
                    log_issue("Navigation Error", "Failed to Login to Planeswalker page")
        except NoSuchElementException:
            log_issue("Login Error", "Failed to Login to Planeswalker page")
        
        print("Testing Login Page...")
        try:
            username_field = driver.find_element(By.ID, "username")
            password_field = driver.find_element(By.ID, "password")
            login_button = driver.find_element(By.ID, "login-button")
            
            username_field.send_keys("test_user")  # Replace with a valid username
            password_field.send_keys("test_password")  # Replace with the corresponding password
            login_button.click()

            # Check if redirected to the correct page
            if "update_planeswalkers" not in driver.current_url:
                print("[Navigation Error] Failed to Login to Planeswalker page")
        except Exception as e:
            print(f"[Error] {e}")


        # Test Editing a Planeswalker
        try:
            edit_button = driver.find_element(By.CSS_SELECTOR, ".edit-button")  # Replace with the actual button's class or ID
            edit_button.click()
            time.sleep(2)
            if "Edit" not in driver.title:  # Adjust based on expected page
                log_issue("Navigation Error", "Failed to open the Planeswalker edit interface")
        except NoSuchElementException:
            log_issue("Element Not Found", "Edit button is missing on the Update Planeswalker page")

    except Exception as e:
        log_issue("Unexpected Error", str(e))

    finally:
        driver.quit()

# Run Tests
test_navigation()
