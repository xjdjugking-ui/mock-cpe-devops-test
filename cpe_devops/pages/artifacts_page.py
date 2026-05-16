from selenium.webdriver.common.by import By
from cpe_devops.base_page import BasePage


class ArtifactsPage(BasePage):
    def load(self):
        self.driver.get(self._url("/artifacts"))

    def register_artifact(self, filename: str, source_type: str = "manual",
                          source_ref: str = "", path: str = "", note: str = ""):
        self._fill("artifact-filename", filename)
        self._select_by_value("artifact-source-type", source_type)
        self._fill("artifact-source-ref", source_ref)
        self._fill("artifact-path", path)
        self._fill("artifact-note", note)
        self._click("register-artifact-button")
        # Wait for form submission to complete before navigating away
        self._find_visible(By.ID, "artifact-message", timeout=20)

    def message(self) -> str:
        try:
            return self._text("artifact-message")
        except Exception:
            return ""
