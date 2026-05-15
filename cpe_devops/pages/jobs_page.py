from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from cpe_devops.base_page import BasePage


class JobsPage(BasePage):
    def load(self):
        self.driver.get(self._url("/jobs"))

    def run_first_job(self):
        sel = Select(self._find(By.ID, "artifact-select"))
        if len(sel.options) > 1:
            sel.select_by_index(1)
        self._click("run-upgrade-job-button")

    def message(self) -> str:
        try:
            return self._text("job-message")
        except Exception:
            return ""

    def status(self) -> str:
        try:
            return self._text("job-status")
        except Exception:
            return ""
