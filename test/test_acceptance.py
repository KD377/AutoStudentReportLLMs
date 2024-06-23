import unittest
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager

class TestAcceptance(unittest.TestCase):

    def setUp(self):
        self.driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))

    # Test sprawdza, czy strona główna aplikacji React zawiera tekst "Automatic student report system"
    def test_homepage(self):
        driver = self.driver
        driver.get("http://localhost:3000")
        self.assertIn("Automatic student report system", driver.page_source)

    # Test sprawdza, czy plik można poprawnie przesłać za pomocą formularza
    def test_file_upload(self):
        driver = self.driver
        driver.get("http://localhost:3000")

        upload_element = driver.find_element(By.CSS_SELECTOR, 'input[type="file"]')
        file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'testfile.docx'))
        upload_element.send_keys(file_path)

        submit_button = driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]')
        submit_button.click()

        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'Report title:')]"))
        )

        self.assertIn("Report title:", driver.page_source)

    # Test sprawdza, czy kliknięcie przycisku "Rate Reports" wyświetla ocenione raporty
    def test_rate_reports(self):
        driver = self.driver
        driver.get("http://localhost:3000")

        rate_button = driver.find_element(By.XPATH, '//button[text()="Rate Reports"]')
        rate_button.click()

        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'All Report Grades')]"))
        )

        self.assertIn("All Report Grades", driver.page_source)

    def tearDown(self):
        self.driver.quit()
