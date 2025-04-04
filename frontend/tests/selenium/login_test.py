import unittest
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

class LoginTest(unittest.TestCase):
    """Selenium tests for the login page of the Golf League Manager application."""
    
    def setUp(self):
        """Set up the test environment."""
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # Run in headless mode
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        
        self.driver = webdriver.Chrome(options=chrome_options)
        self.driver.maximize_window()
        
        # Local development server URL
        self.base_url = "http://localhost:3000"
        
    def tearDown(self):
        """Clean up after the test."""
        self.driver.quit()
        
    def test_login_page_loads(self):
        """Test that the login page loads correctly."""
        self.driver.get(f"{self.base_url}/login")
        
        # Wait for the page to load
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//h1[contains(text(), 'Golf League Manager')]"))
        )
        
        # Check that all elements are present
        self.assertTrue(self.driver.find_element(By.XPATH, "//h1[contains(text(), 'Golf League Manager')]").is_displayed())
        self.assertTrue(self.driver.find_element(By.XPATH, "//h2[contains(text(), 'Sign In')]").is_displayed())
        self.assertTrue(self.driver.find_element(By.ID, "email").is_displayed())
        self.assertTrue(self.driver.find_element(By.ID, "password").is_displayed())
        self.assertTrue(self.driver.find_element(By.XPATH, "//button[contains(text(), 'Sign In')]").is_displayed())
        
    def test_login_with_invalid_credentials(self):
        """Test login with invalid credentials."""
        self.driver.get(f"{self.base_url}/login")
        
        # Wait for the page to load
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, "email"))
        )
        
        # Enter invalid credentials
        self.driver.find_element(By.ID, "email").send_keys("invalid@example.com")
        self.driver.find_element(By.ID, "password").send_keys("wrongpassword")
        
        # Click the login button
        self.driver.find_element(By.XPATH, "//button[contains(text(), 'Sign In')]").click()
        
        # Wait for the error message
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'MuiAlert-root')]"))
        )
        
        # Check that the error message is displayed
        error_message = self.driver.find_element(By.XPATH, "//div[contains(@class, 'MuiAlert-root')]")
        self.assertTrue(error_message.is_displayed())
        
    def test_login_with_valid_credentials(self):
        """
        Test login with valid credentials.
        Note: This test requires a running backend with a valid user.
        It's commented out by default and should be enabled in a proper test environment.
        """
        # This test would be enabled in a real environment with actual Cognito integration
        pass
        
        # self.driver.get(f"{self.base_url}/login")
        
        # # Wait for the page to load
        # WebDriverWait(self.driver, 10).until(
        #     EC.presence_of_element_located((By.ID, "email"))
        # )
        
        # # Enter valid credentials
        # self.driver.find_element(By.ID, "email").send_keys("kevin.cory@mutualofomaha.com")
        # self.driver.find_element(By.ID, "password").send_keys("Welcome123!")
        
        # # Click the login button
        # self.driver.find_element(By.XPATH, "//button[contains(text(), 'Sign In')]").click()
        
        # # Wait for redirection to dashboard
        # WebDriverWait(self.driver, 10).until(
        #     EC.url_contains("/dashboard")
        # )
        
        # # Check that we're on the dashboard page
        # self.assertIn("/dashboard", self.driver.current_url)

if __name__ == "__main__":
    unittest.main()
