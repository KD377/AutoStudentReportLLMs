from selenium import webdriver
from selenium.webdriver.common.by import By
import unittest
import time


class TestCompatibility(unittest.TestCase):

    def setUp(self):
        self.url = "http://localhost:3000"

    def _init_browser(self, browser_name):
        try:
            if browser_name == "safari":
                browser = webdriver.Safari()
            elif browser_name == "chrome":
                browser = webdriver.Chrome()
            elif browser_name == "firefox":
                browser = webdriver.Firefox()
            else:
                raise ValueError("Unsupported browser")
            time.sleep(1)
            return browser
        except Exception as e:
            print(f"Error initializing {browser_name}: {e}")
            return None

    def test_homepage_loads(self):
        for browser_name in ["safari", "chrome", "firefox"]:
            with self.subTest(browser=browser_name):
                browser = self._init_browser(browser_name)
                if browser:
                    browser.get(self.url)
                    time.sleep(2)
                    self.assertIn("React App", browser.title)
                    self.assertIn("Automatic student report system", browser.page_source)
                    browser.quit()

    def test_file_upload_section(self):
        for browser_name in ["safari", "chrome", "firefox"]:
            with self.subTest(browser=browser_name):
                browser = self._init_browser(browser_name)
                if browser:
                    browser.get(self.url)
                    time.sleep(2)
                    self.assertIn("Upload File", browser.page_source)
                    upload_button = browser.find_element(By.XPATH, "//input[@type='file']")
                    self.assertIsNotNone(upload_button)
                    self.assertIn("Upload", browser.page_source)
                    browser.quit()

    def test_report_title_section(self):
        for browser_name in ["safari", "chrome", "firefox"]:
            with self.subTest(browser=browser_name):
                browser = self._init_browser(browser_name)
                if browser:
                    browser.get(self.url)
                    time.sleep(2)
                    self.assertIn("Report title:", browser.page_source)
                    browser.quit()

    def test_rate_and_generate_criteria_section(self):
        for browser_name in ["safari", "chrome", "firefox"]:
            with self.subTest(browser=browser_name):
                browser = self._init_browser(browser_name)
                if browser:
                    browser.get(self.url)
                    time.sleep(2)
                    self.assertIn("Rate and Generate Criteria", browser.page_source)
                    self.assertIn("Generate Criteria", browser.page_source)
                    self.assertIn("1. Experiment Aim", browser.page_source)
                    self.assertIn("2. Theoretical Background", browser.page_source)
                    self.assertIn("3. Research", browser.page_source)
                    self.assertIn("4. Conclusions", browser.page_source)
                    self.assertIn("Save Criteria", browser.page_source)
                    browser.quit()

    def test_all_report_grades_section(self):
        for browser_name in ["safari", "chrome", "firefox"]:
            with self.subTest(browser=browser_name):
                browser = self._init_browser(browser_name)
                if browser:
                    browser.get(self.url)
                    time.sleep(2)
                    self.assertIn("All Report Grades", browser.page_source)
                    browser.quit()


if __name__ == '__main__':
    unittest.main()
