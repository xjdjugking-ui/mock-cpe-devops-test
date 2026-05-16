"""
UI smoke tests — requires Flask server running at http://127.0.0.1:5000.
Start server first: python run.py
Run: pytest tests/ui -v
Run: pytest tests/ui -v -m "not demo_failure"
"""
import os
import sys
import pytest
import allure

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

BASE_URL = os.environ.get("BASE_URL", "http://127.0.0.1:5000")

from cpe_devops.pages.login_page import LoginPage
from cpe_devops.pages.dashboard_page import DashboardPage
from cpe_devops.pages.network_page import NetworkPage
from cpe_devops.pages.upgrade_page import UpgradePage
from cpe_devops.pages.artifacts_page import ArtifactsPage
from cpe_devops.pages.jobs_page import JobsPage
from cpe_devops.pages.stats_page import StatsPage


# ------------------------------------------------------------------
# Login
# ------------------------------------------------------------------
def test_admin_can_login(driver):
    page = LoginPage(driver, BASE_URL)
    page.load()
    page.login("admin", "admin123")
    from selenium.webdriver.support.ui import WebDriverWait
    WebDriverWait(driver, 10).until(lambda d: "/dashboard" in d.current_url)
    assert "/dashboard" in driver.current_url


def test_login_fails_with_wrong_password(driver):
    page = LoginPage(driver, BASE_URL)
    page.load()
    page.login("admin", "wrongpassword")
    assert "/login" in driver.current_url
    assert page.error_message() != ""


# ------------------------------------------------------------------
# Network
# ------------------------------------------------------------------
def test_network_settings_can_be_saved(logged_in_driver):
    page = NetworkPage(logged_in_driver, BASE_URL)
    page.load()
    page.save_network(
        ssid="TestNet-UI",
        password="testpass123",
        mode="dhcp",
        channel="6",
        guest_enabled=False,
    )
    msg = page.message()
    assert msg != "", f"Expected a message but got empty string"
    assert "保存" in msg or "saved" in msg.lower(), f"Unexpected message: {msg!r}"


# ------------------------------------------------------------------
# Firmware validation
# ------------------------------------------------------------------
def test_invalid_firmware_file_is_rejected(logged_in_driver):
    page = UpgradePage(logged_in_driver, BASE_URL)
    page.load()
    page.validate_firmware("bad_firmware.exe")
    msg = page.message()
    assert msg != "", f"Expected rejection message but got empty string"
    assert "rejected" in msg.lower() or "非法" in msg or "不符合" in msg or "格式非法" in msg, \
        f"Unexpected message: {msg!r}"


def test_valid_firmware_file_is_validated(logged_in_driver):
    page = UpgradePage(logged_in_driver, BASE_URL)
    page.load()
    page.validate_firmware("cpe_gateway_v3.0.0.bin")
    msg = page.message()
    assert msg != "", f"Expected validation message but got empty string"
    assert "validated" in msg.lower() or "通过" in msg or "合法" in msg, \
        f"Unexpected message: {msg!r}"


# ------------------------------------------------------------------
# Artifacts
# ------------------------------------------------------------------
def test_artifact_can_be_registered(logged_in_driver):
    page = ArtifactsPage(logged_in_driver, BASE_URL)
    page.load()
    page.register_artifact(
        filename="cpe_gateway_v7.0.0.bin",
        source_type="manual",
        source_ref="ui-test-build",
        path="artifacts/cpe_gateway_v7.0.0.bin",
        note="UI smoke test artifact",
    )
    msg = page.message()
    assert msg != "", f"Expected artifact registration message but got empty string"
    assert "成功" in msg or "success" in msg.lower(), f"Unexpected message: {msg!r}"


# ------------------------------------------------------------------
# Jobs
# ------------------------------------------------------------------
def test_upgrade_job_can_be_run(logged_in_driver):
    # ensure at least one artifact exists
    art_page = ArtifactsPage(logged_in_driver, BASE_URL)
    art_page.load()
    art_page.register_artifact(
        filename="cpe_gateway_v6.0.0.bin",
        source_type="ci",
        source_ref="job-test-build",
    )
    jobs_page = JobsPage(logged_in_driver, BASE_URL)
    jobs_page.load()
    jobs_page.run_first_job()
    msg = jobs_page.message()
    assert msg != "", f"Expected job completion message but got empty string"
    assert "完成" in msg or "passed" in msg.lower() or "成功" in msg, \
        f"Unexpected message: {msg!r}"


# ------------------------------------------------------------------
# Stats
# ------------------------------------------------------------------
def test_stats_page_can_be_opened(logged_in_driver):
    page = StatsPage(logged_in_driver, BASE_URL)
    page.load()
    title = page.title()
    assert title != "", f"Expected a title but got empty string"
    total = page.total_runs()
    assert total is not None, f"Expected total_runs value but got None"


# ------------------------------------------------------------------
# Demo failure — screenshot + Allure attachment sample
# ------------------------------------------------------------------
@pytest.mark.demo_failure
@allure.feature("Network Config")
@allure.story("Save Config Failed")
@allure.severity(allure.severity_level.CRITICAL)
@allure.suite("UI Smoke")
@allure.title("test_network_settings_save_failed")
@allure.description(
    "Verify network config save shows correct message. "
    "Intentionally fails to demonstrate Allure screenshot attachment."
)
def test_demo_failure_for_screenshot_sample(logged_in_driver):
    driver = logged_in_driver

    with allure.step("1. Open login page"):
        driver.get(f"{BASE_URL}/login")

    with allure.step("2. Login as admin/admin123"):
        driver.get(f"{BASE_URL}/dashboard")

    with allure.step("3. Open network settings page"):
        page = NetworkPage(driver, BASE_URL)
        page.load()

    with allure.step("4. Modify IP address and DNS params"):
        driver.find_element("id", "ssid").clear()
        driver.find_element("id", "ssid").send_keys("TestNet-FailDemo")

    with allure.step("5. Click save config button"):
        driver.find_element("id", "save-network-button").click()

    with allure.step("6. Verify message contains saved confirmation"):
        msg = page.message()
        import os as _os
        import tempfile
        ss_path = _os.path.join(tempfile.gettempdir(), "demo_failure.png")
        driver.save_screenshot(ss_path)
        allure.attach.file(
            ss_path,
            name="failure_screenshot.png",
            attachment_type=allure.attachment_type.PNG,
        )
        allure.attach(
            driver.page_source,
            name="page_source.html",
            attachment_type=allure.attachment_type.HTML,
        )
        try:
            logs = driver.get_log("browser")
            log_text = "\n".join(
                f"[{e['level']}] {e['message']}" for e in logs
            ) or "(no console logs)"
        except Exception:
            log_text = "(console log unavailable)"
        allure.attach(
            log_text,
            name="browser_console.log",
            attachment_type=allure.attachment_type.TEXT,
        )
        allure.attach(
            f"actual:   {msg!r}\nexpected: contains 'save failed, please retry'",
            name="assertion_detail",
            attachment_type=allure.attachment_type.TEXT,
        )
        assert "save failed, please retry" in msg, (
            f"expected text to contain 'save failed', but actual message was {msg!r}"
        )