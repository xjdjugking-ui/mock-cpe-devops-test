from cpe_devops.base_page import BasePage


class NetworkPage(BasePage):
    def load(self):
        self.driver.get(self._url("/network"))

    def save_network(self, ssid: str, password: str, mode: str,
                     channel: str, guest_enabled: bool = False):
        self._fill("ssid", ssid)
        self._fill("wifi-password", password)
        self._select_by_value("mode", mode)
        self._select_by_value("channel", channel)
        # checkbox
        cb = self.driver.find_element("id", "guest-wifi")
        if cb.is_selected() != guest_enabled:
            cb.click()
        self._click("save-network-button")

    def message(self) -> str:
        try:
            return self._text("network-message")
        except Exception:
            return ""
