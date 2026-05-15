"""Base page object — shared driver helpers."""
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By


class BasePage:
    def __init__(self, driver, base_url: str = "http://127.0.0.1:5000"):
        self.driver = driver
        self.base_url = base_url.rstrip("/")

    def _url(self, path: str) -> str:
        return self.base_url + path

    def _wait(self, timeout: int = 10):
        return WebDriverWait(self.driver, timeout)

    def _find(self, by, value, timeout: int = 10):
        return self._wait(timeout).until(EC.presence_of_element_located((by, value)))

    def _click(self, element_id: str):
        self._find(By.ID, element_id).click()

    def _fill(self, element_id: str, value: str):
        el = self._find(By.ID, element_id)
        el.clear()
        el.send_keys(value)

    def _text(self, element_id: str) -> str:
        return self._find(By.ID, element_id).text.strip()

    def _select_by_value(self, element_id: str, value: str):
        from selenium.webdriver.support.ui import Select
        Select(self._find(By.ID, element_id)).select_by_value(value)
