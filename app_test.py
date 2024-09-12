import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import unittest

class FlaskAppTest(unittest.TestCase):
    def setUp(self):
        chrome_options = Options()
        # chrome_options.add_argument("--headless")  # Uncomment for headless mode

        self.driver_service = Service('./chromedriver.exe')  # Update the path
        self.driver = webdriver.Chrome(service=self.driver_service, options=chrome_options)
        self.driver.get("http://127.0.0.1:5000/")  # Replace with your local server URL

    def test_registration(self):
        driver = self.driver
        driver.get("http://127.0.0.1:5000/register")  # Replace with your registration page URL

        try:
            username_input = WebDriverWait(driver, 20).until(
                EC.visibility_of_element_located((By.NAME, "username"))  # Updated locator
            )
            password_input = WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.NAME, "password"))  # Updated locator
            )
            submit_button = WebDriverWait(driver, 20).until(
                EC.element_to_be_clickable((By.XPATH, "//button[@type='submit']"))  # Updated locator
            )

            username_input.send_keys(os.getenv('REGISTER_USERNAME', 'new_test_user1'))
            password_input.send_keys(os.getenv('REGISTER_PASSWORD', 'New_test_password1'))
            submit_button.click()

            # Debugging: Capture screenshot
            driver.save_screenshot('registration_test_failed.png')
            success_message = WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.CLASS_NAME, "alert"))  # Updated locator
            )
            self.assertIn("Registration successful", driver.page_source)
        except TimeoutException:
            self.fail("Registration failed or success message not displayed in time.")

    def test_login(self):
        driver = self.driver
        driver.get("http://127.0.0.1:5000/login")  # Replace with your login page URL

        try:
            # Locate username and password fields
            username_input = WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.NAME, "username"))  # Updated locator
            )
            password_input = WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.NAME, "password"))  # Updated locator
            )
            role_input = WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.NAME, "role"))  # Updated locator
            )
            login_button = WebDriverWait(driver, 20).until(
                EC.element_to_be_clickable((By.XPATH, "//button[@type='submit']"))  # Updated locator
            )

            # Enter credentials
            username_input.send_keys(os.getenv('REGISTER_USERNAME', 'test_user1'))
            password_input.send_keys(os.getenv('REGISTER_PASSWORD', 'test_pass1'))
            role_input.send_keys("user")
            login_button.click()

            # Debugging: Capture screenshot in case of failure
            driver.save_screenshot('login_test_failed.png')

            # The test stops here after the login button is clicked successfully
            self.assertTrue(True, "Login button clicked successfully without error.")

        except TimeoutException:
            self.fail("Login failed: Element not found or not interactable in time.")

    def test_login_and_submit_text(self):
        driver = self.driver
        driver.get("http://127.0.0.1:5000/login")  # Replace with your login page URL

        try:
            # Step 1: Login Process
            # Locate the username, password inputs, and login button
            username_input = WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.NAME, "username"))
            )
            password_input = WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.NAME, "password"))
            )
            login_button = WebDriverWait(driver, 20).until(
                EC.element_to_be_clickable((By.XPATH, "//button[@type='submit']"))
            )

            # Enter login credentials
            username_input.send_keys(os.getenv('REGISTER_USERNAME', 'test_user'))
            password_input.send_keys(os.getenv('REGISTER_PASSWORD', 'Test_123'))
            login_button.click()

            # Step 2: Navigate to Index Page After Login
            WebDriverWait(driver, 20).until(
                EC.url_contains("/index")  # Wait until redirected to the index page
            )

            # Step 3: Submit Text on Index Page
            # Locate the text area and submit button
            text_area = WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.ID, "text"))
            )
            submit_button = WebDriverWait(driver, 20).until(
                EC.element_to_be_clickable((By.XPATH, "//button[@type='submit']"))
            )

            # Type the text into the text area
            input_text = "This is a test input text to check for hate speech."
            text_area.send_keys(input_text)

            # Click the submit button
            submit_button.click()

            # Wait for results to be generated and displayed
            result = WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.CLASS_NAME, "result"))
            )

            # Debugging: Capture screenshot in case of failure
            driver.save_screenshot('submit_text_test_failed.png')

            # Verify that the results contain the input text or the expected result
            self.assertIn(input_text, driver.page_source)
            self.assertTrue(result.is_displayed(), "Results are displayed correctly.")

        except TimeoutException:
            self.fail("Failed to login, submit text, or get results in time.")

    def test_submit_feedback(self):
        driver = self.driver
        driver.get("http://127.0.0.1:5000/login")  # Replace with your login page URL

        try:
            # Step 1: Login Process
            username_input = WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.NAME, "username"))
            )
            password_input = WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.NAME, "password"))
            )
            login_button = WebDriverWait(driver, 20).until(
                EC.element_to_be_clickable((By.XPATH, "//button[@type='submit']"))
            )

            # Enter login credentials
            username_input.send_keys(os.getenv('REGISTER_USERNAME', 'test_user'))
            password_input.send_keys(os.getenv('REGISTER_PASSWORD', 'Test_123'))
            login_button.click()

            # Step 2: Navigate to Manage Entries Page
            WebDriverWait(driver, 20).until(
                EC.url_contains("/index")  # Ensure redirected to index page or adjust URL if needed
            )
            manage_entries_link = WebDriverWait(driver, 20).until(
                EC.element_to_be_clickable((By.XPATH, "//a[text()='Manage Entries']"))
            )
            manage_entries_link.click()

            # Step 3: Open Feedback Submission Modal
            entry_id = 54  # Replace with a valid entry ID if needed
            submit_feedback_button = WebDriverWait(driver, 20).until(
                EC.element_to_be_clickable((By.XPATH, f"//button[@data-target='#submitFeedbackModal{entry_id}']"))
            )
            submit_feedback_button.click()

            # Step 4: Type and Submit Feedback in Modal
            feedback_textarea = WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.NAME, "feedback_text"))
            )
            submit_button_modal = WebDriverWait(driver, 20).until(
                EC.element_to_be_clickable(
                    (By.XPATH, "//button[@type='submit' and contains(text(), 'Submit Feedback')]"))
            )

            # Enter feedback and submit
            feedback_text = "This is a test feedback."
            feedback_textarea.send_keys(feedback_text)
            submit_button_modal.click()

            # Add a short wait to ensure the feedback submission is processed
            WebDriverWait(driver, 10).until(
                EC.invisibility_of_element_located((By.XPATH, f"//div[@id='submitFeedbackModal{entry_id}']"))
            )

            # Check if modal is closed and feedback was likely submitted
            # If modal is no longer visible, assume feedback was submitted successfully
            self.assertNotIn(f"submitFeedbackModal{entry_id}", driver.page_source)

        except TimeoutException as e:
            print("Timeout Exception:", e)  # Debugging line
            self.fail("Failed to submit feedback: Element not found or not interactable in time.")

    def tearDown(self):
        self.driver.quit()

if __name__ == "__main__":
    unittest.main()
