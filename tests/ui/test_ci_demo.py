"""Stable UI demo tests for Jenkins and Allure presentation."""
import os
import tempfile

import allure
from selenium.webdriver.support.ui import WebDriverWait

from cpe_devops.pages.login_page import LoginPage
from cpe_devops.pages.network_page import NetworkPage
from cpe_devops.pages.stats_page import StatsPage


BASE_URL = os.environ.get("BASE_URL", "http://127.0.0.1:5000")


def attach_page(driver, name: str) -> None:
    path = os.path.join(tempfile.gettempdir(), f"{name}.png")
    driver.save_screenshot(path)
    allure.attach.file(
        path,
        name=f"{name}.png",
        attachment_type=allure.attachment_type.PNG,
    )
    allure.attach(
        driver.page_source,
        name=f"{name}.html",
        attachment_type=allure.attachment_type.HTML,
    )


@allure.feature("Web Management")
@allure.story("Admin login")
@allure.severity(allure.severity_level.BLOCKER)
@allure.suite("CI Demo")
@allure.title("管理员可以登录 Mock CPE 管理后台")
def test_ci_admin_login(driver):
    with allure.step("打开登录页"):
        page = LoginPage(driver, BASE_URL)
        page.load()

    with allure.step("输入 admin/admin123 并提交"):
        page.login("admin", "admin123")

    with allure.step("校验进入仪表盘"):
        WebDriverWait(driver, 10).until(lambda d: "/dashboard" in d.current_url)
        attach_page(driver, "dashboard_after_login")
        assert "/dashboard" in driver.current_url


@allure.feature("Network Config")
@allure.story("Save wireless settings")
@allure.severity(allure.severity_level.CRITICAL)
@allure.suite("CI Demo")
@allure.title("网络配置可以保存并返回提示")
def test_ci_network_settings_saved(logged_in_driver):
    with allure.step("打开网络设置页面"):
        page = NetworkPage(logged_in_driver, BASE_URL)
        page.load()

    with allure.step("修改 SSID、密码、模式和信道"):
        page.save_network(
            ssid="MockCPE-CI-Demo",
            password="testpass123",
            mode="dhcp",
            channel="6",
            guest_enabled=False,
        )

    with allure.step("校验保存提示并附加截图"):
        msg = page.message()
        attach_page(logged_in_driver, "network_settings_saved")
        allure.attach(
            f"actual message: {msg!r}",
            name="assertion_detail.txt",
            attachment_type=allure.attachment_type.TEXT,
        )
        assert msg != ""


@allure.feature("Dashboard")
@allure.story("Quality statistics")
@allure.severity(allure.severity_level.NORMAL)
@allure.suite("CI Demo")
@allure.title("统计页面可以展示测试运行数据")
def test_ci_stats_page(logged_in_driver):
    with allure.step("打开统计页面"):
        page = StatsPage(logged_in_driver, BASE_URL)
        page.load()

    with allure.step("读取总运行次数和页面标题"):
        title = page.title()
        total_runs = page.total_runs()
        attach_page(logged_in_driver, "stats_page")
        allure.attach(
            f"title: {title!r}\ntotal_runs: {total_runs!r}",
            name="stats_values.txt",
            attachment_type=allure.attachment_type.TEXT,
        )
        assert title != ""
        assert total_runs is not None
