from cpe_devops.base_page import BasePage


class UpgradePage(BasePage):
    def load(self):
        self.driver.get(self._url("/upgrade"))

    def validate_firmware(self, filename: str):
        self._fill(self.sel["firmware_filename"], filename)
        self._click("validate-firmware-button")

    def status(self) -> str:
        try:
            return self._text("upgrade-status")
        except Exception:
            return ""

    def message(self) -> str:
        try:
            return self._text("upgrade-message")
        except Exception:
            return ""
