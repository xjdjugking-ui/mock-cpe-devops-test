from selenium.webdriver.common.by import By
from cpe_devops.base_page import BasePage


class LoginPage(BasePage):
    def load(self):
        self.driver.get(self._url("/login"))

    def login(self, username: str, password: str):
        self._fill(self.sel["username"], username)
        self._fill(self.sel["password"], password)
        self._click(self.sel["login_button"])

    def error_message(self) -> str:
        try:
            return self._text("login-error")
        except Exception:
            return ""
