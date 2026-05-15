from cpe_devops.base_page import BasePage


class DashboardPage(BasePage):
    def title(self) -> str:
        return self._text("dashboard-title")

    def welcome_text(self) -> str:
        try:
            return self._text("welcome-banner")
        except Exception:
            return ""

    def firmware_version(self) -> str:
        return self._text("firmware-version")

    def wan_status(self) -> str:
        return self._text("wan-status")
