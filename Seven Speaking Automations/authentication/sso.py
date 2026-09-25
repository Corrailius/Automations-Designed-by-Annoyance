import selenium.webdriver.support.ui
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC


class SSO:
    def __init__(self, driver, email, password):
        self.driver = driver
        self.email = email
        self.password = password

    def reject_cookies(self):
        wait = selenium.webdriver.support.ui.WebDriverWait(self.driver, 5)

        try:
            reject_button = wait.until(
                EC.element_to_be_clickable((By.ID, "cky-btn-reject"))
            )

            reject_button.click()

        except TimeoutException:
            pass

    def login(self):
        wait = selenium.webdriver.support.ui.WebDriverWait(self.driver, 30)

        print("Waiting for username field...")

        email_field = wait.until(EC.presence_of_element_located((By.NAME, "username")))

        print("Entering email...")
        email_field.send_keys(self.email)

        print("Waiting for SSO button...")

        sso_button = wait.until(
            EC.element_to_be_clickable(
                (
                    By.CSS_SELECTOR,
                    'a[href="https://lms.7speaking.com/ynov/sso/index.php"]',
                )
            )
        )

        print("Opening school SSO...")
        sso_button.click()

        print("Waiting for SSO email page...")

        sso_email = wait.until(EC.presence_of_element_located((By.ID, "username")))

        print("Entering SSO email...")
        sso_email.send_keys(self.email)
        sso_email.send_keys(Keys.ENTER)

        print("Waiting for SSO password page...")

        sso_password = wait.until(EC.presence_of_element_located((By.ID, "password")))

        print("Entering SSO password...")
        sso_password.send_keys(self.password)
        sso_password.send_keys(Keys.ENTER)

        print("Waiting for 7Speaking...")

        wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "img[alt='Level_badge']"))
        )

        self.reject_cookies()

        print("Authentication successful.")
