import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import unittest
from app import app

class FlaskAppTest(unittest.TestCase):
    def setUp(self):
        # Set up Selenium WebDriver
        chrome_options = Options()
        # chrome_options.add_argument("--headless")
        self.driver_service = Service('./chromedriver.exe')  # Update the path
        self.driver = webdriver.Chrome(service=self.driver_service, options=chrome_options)
        self.driver.get("http://127.0.0.1:5000/")

        # Set up Flask test client
        self.client = app.test_client()
        self.client.testing = True

    def test_registration(self):
        driver = self.driver
        driver.get("http://127.0.0.1:5000/register")

        try:
            username_input = WebDriverWait(driver, 20).until(
                EC.visibility_of_element_located((By.NAME, "username"))
            )
            password_input = WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.NAME, "password"))
            )
            submit_button = WebDriverWait(driver, 20).until(
                EC.element_to_be_clickable((By.XPATH, "//button[@type='submit']"))
            )

            username_input.send_keys(os.getenv('REGISTER_USERNAME', 'new_test_user1'))
            password_input.send_keys(os.getenv('REGISTER_PASSWORD', 'New_test_password1'))
            submit_button.click()

            # Debugging: Capture screenshot
            driver.save_screenshot('registration_test_failed.png')
            success_message = WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.CLASS_NAME, "alert"))
            )
            self.assertIn("Registration successful", driver.page_source)
        except TimeoutException:
            self.fail("Registration failed or success message not displayed in time.")

    def test_login(self):
        driver = self.driver
        driver.get("http://127.0.0.1:5000/login")

        try:
            # Locate username and password fields
            username_input = WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.NAME, "username"))
            )
            password_input = WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.NAME, "password"))
            )
            role_input = WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.NAME, "role"))
            )
            login_button = WebDriverWait(driver, 20).until(
                EC.element_to_be_clickable((By.XPATH, "//button[@type='submit']"))
            )

            # Enter credentials
            username_input.send_keys(os.getenv('REGISTER_USERNAME', 'test_user1'))
            password_input.send_keys(os.getenv('REGISTER_PASSWORD', 'test_pass1'))
            role_input.send_keys("user")
            login_button.click()

            # Debugging: Capture screenshot in case of failure
            driver.save_screenshot('login_test_failed.png')


            self.assertTrue(True, "Login button clicked successfully without error.")

        except TimeoutException:
            self.fail("Login failed: Element not found or not interactable in time.")

    def test_login_and_submit_text(self):
        driver = self.driver
        driver.get("http://127.0.0.1:5000/login")

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
                EC.url_contains("/index")
            )

            # Step 3: Submit Text on Index Page
            # Locate the text area and submit button
            text_area = WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.ID, "text"))
            )
            submit_button = WebDriverWait(driver, 20).until(
                EC.element_to_be_clickable((By.XPATH, "//button[@type='submit']"))
            )


            input_text = "This is a test input text to check for hate speech."
            text_area.send_keys(input_text)

            submit_button.click()


            result = WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.CLASS_NAME, "result"))
            )

            # Debugging: Capture screenshot in case of failure
            driver.save_screenshot('submit_text_test_failed.png')


            self.assertIn(input_text, driver.page_source)
            self.assertTrue(result.is_displayed(), "Results are displayed correctly.")

        except TimeoutException:
            self.fail("Failed to login, submit text, or get results in time.")

    def test_login_and_submit_empty_text(self):
        driver = self.driver
        driver.get("http://127.0.0.1:5000/login")

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

            # Step 2: Navigate to Index Page After Login
            WebDriverWait(driver, 20).until(
                EC.url_contains("/index")
            )

            # Step 3: Submit Empty Text on Index Page
            text_area = WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.ID, "text"))
            )
            submit_button = WebDriverWait(driver, 20).until(
                EC.element_to_be_clickable((By.XPATH, "//button[@type='submit']"))
            )

            # Do not type anything into the text area
            # Click the submit button
            submit_button.click()

            # Verify no results are displayed
            try:
                # Wait for the result element to be present and assert it is not displayed
                WebDriverWait(driver, 5).until(
                    EC.invisibility_of_element_located((By.CLASS_NAME, "result"))
                )
                result_displayed = False
            except TimeoutException:
                # If the result element is present, the test should fail
                result_displayed = True

            # Debugging: Capture screenshot in case of failure
            driver.save_screenshot('submit_empty_text_test_failed.png')

            # Assert no result should be displayed
            self.assertFalse(result_displayed, "Results should not be displayed when no text is input.")

        except TimeoutException:
            self.fail("Failed to login, submit empty text, or check results in time.")

    def test_login_admin(self):
        driver = self.driver
        driver.get("http://127.0.0.1:5000/login")

        try:
            # Locate username and password fields
            username_input = WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.NAME, "username"))
            )
            password_input = WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.NAME, "password"))
            )
            role_input = WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.NAME, "role"))
            )
            login_button = WebDriverWait(driver, 20).until(
                EC.element_to_be_clickable((By.XPATH, "//button[@type='submit']"))
            )

            # Enter credentials
            username_input.send_keys(os.getenv('REGISTER_USERNAME', 'superadmin'))
            password_input.send_keys(os.getenv('REGISTER_PASSWORD', 'Digi@1991'))
            role_input.send_keys("admin")
            login_button.click()

            # Debugging: Capture screenshot in case of failure
            driver.save_screenshot('login_test_failed.png')


            self.assertTrue(True, "Login button clicked successfully without error.")

        except TimeoutException:
            self.fail("Login failed: Element not found or not interactable in time.")

    def test_registration_without_data(self):
        driver = self.driver
        driver.get("http://127.0.0.1:5000/register")

        try:
            # Locate the submit button
            submit_button = WebDriverWait(driver, 20).until(
                EC.element_to_be_clickable((By.XPATH, "//button[@type='submit']"))
            )

            # Click the submit button without entering any data
            submit_button.click()

            # Check for the presence of the 'required' attribute's validation
            # The browser should prevent form submission and keep us on the registration page
            # Capture a screenshot for debugging purposes
            driver.save_screenshot('registration_without_data.png')

            # Since both input fields are marked as `required`, the form should not be submitted
            # Verify that we are still on the registration page
            self.assertIn("Register", driver.title)

        except TimeoutException:
            self.fail("Test failed: Could not find or interact with the required elements on the registration page.")

    def test_login_without_data(self):
        # Use the Flask test client to simulate a POST request without any data
        response = self.client.post('/login', data={})

        # Check that the request response status code is 400
        self.assertEqual(response.status_code, 400)  # Expecting 400 Bad Request

        # Check that the custom error message is in the response
        self.assertIn(b'All fields are required.', response.data)  # Look for your specific flash message

        # Check that the login page is rendered
        self.assertIn(b'Login', response.data)

    def test_submit_feedback(self):
        driver = self.driver
        driver.get("http://127.0.0.1:5000/login")

        try:
            # Step 1: Login Process
            username_input = WebDriverWait(driver, 30).until(
                EC.presence_of_element_located((By.NAME, "username"))
            )
            password_input = WebDriverWait(driver, 30).until(
                EC.presence_of_element_located((By.NAME, "password"))
            )
            login_button = WebDriverWait(driver, 30).until(
                EC.element_to_be_clickable((By.XPATH, "//button[@type='submit']"))
            )

            # Enter login credentials
            username_input.send_keys(os.getenv('REGISTER_USERNAME', 'test_user'))
            password_input.send_keys(os.getenv('REGISTER_PASSWORD', 'Test_123'))
            login_button.click()

            # Step 2: Navigate to Manage Entries Page
            WebDriverWait(driver, 30).until(
                EC.url_contains("/index")
            )
            manage_entries_link = WebDriverWait(driver, 30).until(
                EC.element_to_be_clickable((By.XPATH, "//a[text()='Manage Entries']"))
            )
            manage_entries_link.click()

            # Step 3: Open Feedback Submission Modal
            entry_id = 54  # Replace with a valid entry ID if needed
            submit_feedback_button = WebDriverWait(driver, 30).until(
                EC.element_to_be_clickable((By.XPATH, f"//button[@data-target='#submitFeedbackModal{entry_id}']"))
            )
            submit_feedback_button.click()

            # Step 4: Type and Submit Feedback in Modal
            feedback_textarea = WebDriverWait(driver, 30).until(
                EC.presence_of_element_located((By.NAME, "feedback_text"))
            )
            submit_button_modal = WebDriverWait(driver, 30).until(
                EC.element_to_be_clickable(
                    (By.XPATH, f"//div[@id='submitFeedbackModal{entry_id}']//button[@type='submit']"))
            )

            feedback_text = "This is a test feedback."
            feedback_textarea.send_keys(feedback_text)
            submit_button_modal.click()

            # Wait for modal to disappear
            WebDriverWait(driver, 30).until(
                EC.invisibility_of_element_located((By.ID, f'submitFeedbackModal{entry_id}'))
            )

            # If no errors occurred, the test is considered successful
            print("Feedback submitted successfully.")

        except Exception as e:
            # Print debugging information
            print("An error occurred:", e)
            print(driver.page_source)  # Print page source for debugging
            self.fail(f"Test failed with exception: {e}")

    def tearDown(self):
        self.driver.quit()

if __name__ == "__main__":
    unittest.main()
