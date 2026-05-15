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

    def message(self) -> str:
        try:
            return self._text("artifact-message")
        except Exception:
            return ""
