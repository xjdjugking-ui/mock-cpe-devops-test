from selenium.webdriver.common.by import By
from cpe_devops.base_page import BasePage


class LoginPage(BasePage):
    def load(self):
        self.driver.get(self._url("/login"))

    def login(self, username: str, password: str):
        self._fill("username", username)
        self._fill("password", password)
        self._click("login-button")

    def error_message(self) -> str:
        try:
            return self._text("login-error")
        except Exception:
            return ""
