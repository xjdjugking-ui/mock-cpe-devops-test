from cpe_devops.base_page import BasePage


class StatsPage(BasePage):
    def load(self):
        self.driver.get(self._url("/stats"))

    def title(self) -> str:
        return self._text("stats-title")

    def pass_rate(self) -> str:
        return self._text("pass-rate")

    def total_runs(self) -> str:
        return self._text("total-runs")
