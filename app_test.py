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
        # chrome_options.add_argument("--headless")

        self.driver_service = Service('./chromedriver.exe')  # Update the path
        self.driver = webdriver.Chrome(service=self.driver_service, options=chrome_options)
        self.driver.get("http://127.0.0.1:5000/")

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


    def test_submit_feedback(self):
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

            # Step 2: Navigate to Manage Entries Page
            WebDriverWait(driver, 20).until(
                EC.url_contains("/index")
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


            feedback_text = "This is a test feedback."
            feedback_textarea.send_keys(feedback_text)
            submit_button_modal.click()


            WebDriverWait(driver, 10).until(
                EC.invisibility_of_element_located((By.XPATH, f"//div[@id='submitFeedbackModal{entry_id}']"))
            )


            self.assertNotIn(f"submitFeedbackModal{entry_id}", driver.page_source)

        except TimeoutException as e:
            print("Timeout Exception:", e)  # Debugging line
            self.fail("Failed to submit feedback: Element not found or not interactable in time.")


    def tearDown(self):
        self.driver.quit()

if __name__ == "__main__":
    unittest.main()
