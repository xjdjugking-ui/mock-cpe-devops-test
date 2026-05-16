"""UI Regression Parametrize Tests — ≥200 test cases via pytest parametrize.

Uses the Page Object Model with multi-model device profiles to validate
the CPE Web Management Console across 3 device models.

Total parametrize-generated cases target: ≥ 200.
"""
import os
import sys
import pytest
import allure

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

BASE_URL = os.environ.get("BASE_URL", "http://127.0.0.1:5000")

from cpe_devops.pages.login_page import LoginPage
from cpe_devops.pages.network_page import NetworkPage
from cpe_devops.pages.upgrade_page import UpgradePage
from cpe_devops.pages.artifacts_page import ArtifactsPage
from cpe_devops.pages.jobs_page import JobsPage
from cpe_devops.pages.dashboard_page import DashboardPage
from cpe_devops.pages.stats_page import StatsPage

PROFILES = ["cpe_gw_x300", "cpe_gw_x500", "mifi_m3"]


# ==================================================================
# 1. Login — Valid Credentials (3 cases)
# ==================================================================
@pytest.mark.parametrize("model", PROFILES)
@allure.feature("UI Regression")
@allure.story("Login Valid Credentials")
def test_login_valid_regression(driver, model):
    """Valid admin credentials login across all device models."""
    page = LoginPage(driver, BASE_URL, model=model)
    page.load()
    page.login("admin", "admin123")
    from selenium.webdriver.support.ui import WebDriverWait
    WebDriverWait(driver, 10).until(lambda d: "/dashboard" in d.current_url)
    assert "/dashboard" in driver.current_url


# ==================================================================
# 2. Login — Invalid Credentials (12 cases: 4 combos × 3 models)
# ==================================================================
LOGIN_INVALID_COMBOS = [
    ("admin", "wrongpassword"),
    ("unknown", "admin123"),
    ("", "admin123"),
    ("admin", ""),
]


@pytest.mark.parametrize("username,password,model", [
    (u, p, m) for u, p in LOGIN_INVALID_COMBOS for m in PROFILES
])
@allure.feature("UI Regression")
@allure.story("Login Invalid Credentials")
def test_login_invalid_regression(driver, username, password, model):
    """Invalid login credentials should show error and remain on login page."""
    page = LoginPage(driver, BASE_URL, model=model)
    page.load()
    page.login(username, password)
    # Should stay on login page
    assert "/login" in driver.current_url or "/dashboard" not in driver.current_url


# ==================================================================
# 3. Network Config — Varied Parameters (60 cases: 20 combos × 3 models)
# ==================================================================
NETWORK_COMBOS = [
    # ssid, mode, channel, guest_enabled
    ("HomeWiFi", "dhcp", "6", False),
    ("Office-Net", "static", "11", False),
    ("IoT_Network", "dhcp", "1", True),
    ("Guest-Zone", "static", "36", True),
    ("MyNetwork", "dhcp", "40", False),
    ("短名测试", "static", "6", False),
    ("CPE_5GHz", "dhcp", "36", True),
    ("Lab_Test", "static", "11", True),
    ("Dev_Net", "dhcp", "1", False),
    ("Prod_WiFi", "static", "40", False),
    ("Alpha-Net", "dhcp", "6", True),
    ("Beta_Zone", "static", "11", False),
    ("Gamma_Mesh", "dhcp", "36", False),
    ("Delta_AP", "static", "1", True),
    ("Epsilon", "dhcp", "40", True),
    ("Zeta_Link", "static", "6", False),
    ("Eta_Cloud", "dhcp", "11", True),
    ("Theta_LAN", "static", "36", False),
    ("Iota_WAN", "dhcp", "1", True),
    ("Kappa_P2P", "static", "40", True),
]


@pytest.mark.parametrize("ssid,mode,channel,guest,model", [
    (ssid, mode, ch, guest, m) for (ssid, mode, ch, guest) in NETWORK_COMBOS for m in PROFILES
])
@allure.feature("UI Regression")
@allure.story("Network Config Varied Parameters")
def test_network_regression(logged_in_driver, ssid, mode, channel, guest, model):
    """Network configuration saved with varied SSID/mode/channel/guest combinations."""
    page = NetworkPage(logged_in_driver, BASE_URL, model=model)
    page.load()
    page.save_network(ssid=ssid, password="testpass123", mode=mode,
                      channel=channel, guest_enabled=guest)
    msg = page.message()
    assert msg != "", f"[{model}] Expected network save message but got empty"
    assert "保存" in msg, f"[{model}] Unexpected message: {msg!r}"


# ==================================================================
# 4. Network Config — Special SSID Characters (15 cases: 5 SSIDs × 3 models)
# ==================================================================
SPECIAL_SSIDS = [
    "WiFi-With-Dashes",
    "WiFi_With_Underscores",
    "WiFi With Spaces",
    "A" * 32,       # max length SSID
    "xYz12",        # mixed case short
]


@pytest.mark.parametrize("ssid,model", [
    (s, m) for s in SPECIAL_SSIDS for m in PROFILES
])
@allure.feature("UI Regression")
@allure.story("Network Special SSID Characters")
def test_network_special_ssid_regression(logged_in_driver, ssid, model):
    """Network save with special SSID characters (dashes, spaces, max-length)."""
    page = NetworkPage(logged_in_driver, BASE_URL, model=model)
    page.load()
    page.save_network(ssid=ssid, password="pass!@#$", mode="dhcp",
                      channel="6", guest_enabled=False)
    msg = page.message()
    assert msg != "", f"[{model}] Expected network save message for SSID {ssid!r}"
    assert "保存" in msg, f"[{model}] Unexpected message: {msg!r}"


# ==================================================================
# 5. Firmware Validation — Valid Filenames (15 cases: 5 × 3 models)
# ==================================================================
VALID_FIRMWARE = [
    ("cpe_gateway_v1.0.0.bin", "1.0.0"),
    ("cpe_gateway_v2.1.0.bin", "2.1.0"),
    ("cpe_gateway_v9.9.9.bin", "9.9.9"),
    ("cpe_gateway_v10.20.30.bin", "10.20.30"),
    ("cpe_gateway_v0.0.1.bin", "0.0.1"),
]


@pytest.mark.parametrize("filename,expected_version,model", [
    (fn, ver, m) for (fn, ver) in VALID_FIRMWARE for m in PROFILES
])
@allure.feature("UI Regression")
@allure.story("Firmware Valid Filenames")
def test_firmware_valid_regression(logged_in_driver, filename, expected_version, model):
    """Valid firmware filenames should be accepted across models."""
    page = UpgradePage(logged_in_driver, BASE_URL, model=model)
    page.load()
    page.validate_firmware(filename)
    msg = page.message()
    assert msg != "", f"[{model}] Expected validation message for {filename!r}"
    assert "validated" in msg.lower() or "通过" in msg or "合法" in msg or "已验证" in msg, \
        f"[{model}] Unexpected message for valid firmware {filename!r}: {msg!r}"


# ==================================================================
# 6. Firmware Validation — Invalid Filenames (21 cases: 7 × 3 models)
# ==================================================================
INVALID_FIRMWARE = [
    "bad_firmware.zip",
    "firmware.bin",
    "cpe_gateway_v2.1.bin",          # missing patch version
    "cpe_gateway_vA.B.C.bin",        # non-numeric version
    "",                               # empty
    "CPE_GATEWAY_V1.0.0.BIN",        # uppercase (case sensitive pattern)
    "cpe_gateway_v1.0.0.exe",        # wrong extension
]


@pytest.mark.parametrize("filename,model", [
    (fn, m) for fn in INVALID_FIRMWARE for m in PROFILES
])
@allure.feature("UI Regression")
@allure.story("Firmware Invalid Filenames")
def test_firmware_invalid_regression(logged_in_driver, filename, model):
    """Invalid firmware filenames should be rejected across models."""
    page = UpgradePage(logged_in_driver, BASE_URL, model=model)
    page.load()
    page.validate_firmware(filename)
    msg = page.message()
    # Rejected firmware still shows a response on the page
    assert msg != "", f"[{model}] Expected rejection message for {filename!r}"
    assert "rejected" in msg.lower() or "拒绝" in msg or "不合" in msg or "已拒绝" in msg, \
        f"[{model}] Expected rejection for {filename!r}, got: {msg!r}"


# ==================================================================
# 7. Artifact Registration — Valid (45 cases: 15 combos × 3 models)
# ==================================================================
ARTIFACT_COMBOS = [
    # (filename, source_type, source_ref, note)
    ("cpe_gateway_v1.0.0.bin", "local", "", ""),
    ("cpe_gateway_v2.1.0.bin", "ci", "build-101", "CI build"),
    ("cpe_gateway_v3.0.0.bin", "manual", "manual-upload", "手动上传"),
    ("cpe_gateway_v4.0.0.bin", "ci", "jenkins-42", ""),
    ("cpe_gateway_v5.0.1.bin", "local", "", "local dev build"),
    ("cpe_gateway_v6.6.6.bin", "manual", "ops-team", "运维团队上传"),
    ("cpe_gateway_v7.0.0.bin", "ci", "pipeline-777", "CI/CD nightly"),
    ("cpe_gateway_v8.1.2.bin", "local", "", ""),
    ("cpe_gateway_v9.9.9.bin", "manual", "release-999", "正式发布版本"),
    ("cpe_gateway_v10.0.0.bin", "ci", "build-1000", ""),
    ("cpe_gateway_v11.22.33.bin", "local", "", "pre-release"),
    ("cpe_gateway_v12.0.0.bin", "manual", "field-engineer", "现场工程师"),
    ("cpe_gateway_v13.1.4.bin", "ci", "build-1314", "hotfix build"),
    ("cpe_gateway_v14.0.0.bin", "local", "", ""),
    ("cpe_gateway_v15.0.0.bin", "manual", "qa-signoff", "QA 签核版本"),
]


@pytest.mark.parametrize("filename,source_type,source_ref,note,model", [
    (fn, st, sr, n, m) for (fn, st, sr, n) in ARTIFACT_COMBOS for m in PROFILES
])
@allure.feature("UI Regression")
@allure.story("Artifact Registration Valid")
def test_artifact_regression(logged_in_driver, filename, source_type,
                             source_ref, note, model):
    """Valid artifact registration across varied source types and models."""
    page = ArtifactsPage(logged_in_driver, BASE_URL, model=model)
    page.load()
    page.register_artifact(
        filename=filename,
        source_type=source_type,
        source_ref=source_ref,
        path=f"artifacts/{filename}",
        note=note,
    )
    msg = page.message()
    assert msg != "", f"[{model}] Expected artifact message for {filename!r}"
    assert "成功" in msg or "success" in msg.lower(), \
        f"[{model}] Expected success for {filename!r}, got: {msg!r}"


# ==================================================================
# 8. Artifact Registration — Invalid (12 cases: 4 × 3 models)
# ==================================================================
INVALID_ARTIFACT_FILENAMES = [
    "bad_firmware.exe",
    "not_a_firmware.zip",
    "random_file.txt",
    "",
]


@pytest.mark.parametrize("filename,model", [
    (fn, m) for fn in INVALID_ARTIFACT_FILENAMES for m in PROFILES
])
@allure.feature("UI Regression")
@allure.story("Artifact Registration Invalid")
def test_artifact_invalid_regression(logged_in_driver, filename, model):
    """Invalid artifact filenames should be rejected across models."""
    page = ArtifactsPage(logged_in_driver, BASE_URL, model=model)
    page.load()
    page.register_artifact(
        filename=filename,
        source_type="manual",
    )
    msg = page.message()
    assert msg != "", f"[{model}] Expected rejection for {filename!r}"
    assert "失败" in msg or "error" in msg.lower() or "拒绝" in msg or "不合" in msg, \
        f"[{model}] Expected rejection for {filename!r}, got: {msg!r}"


# ==================================================================
# 9. Dashboard Display (3 cases: 1 per model)
# ==================================================================
@pytest.mark.parametrize("model", PROFILES)
@allure.feature("UI Regression")
@allure.story("Dashboard Display")
def test_dashboard_display_regression(logged_in_driver, model):
    """Dashboard page loads and shows key elements across models."""
    page = DashboardPage(logged_in_driver, BASE_URL, model=model)
    logged_in_driver.get(page._url("/dashboard"))
    title = page.title()
    assert title != "", f"[{model}] Dashboard title is empty"
    fw = page.firmware_version()
    assert fw != "", f"[{model}] Firmware version is empty"
    wan = page.wan_status()
    assert wan != "", f"[{model}] WAN status is empty"


# ==================================================================
# 10. Stats Page Display (3 cases: 1 per model)
# ==================================================================
@pytest.mark.parametrize("model", PROFILES)
@allure.feature("UI Regression")
@allure.story("Stats Page Display")
def test_stats_display_regression(logged_in_driver, model):
    """Stats page loads and shows summary metrics across models."""
    page = StatsPage(logged_in_driver, BASE_URL, model=model)
    page.load()
    title = page.title()
    assert title != "", f"[{model}] Stats title is empty"
    pr = page.pass_rate()
    assert pr != "", f"[{model}] Pass rate is empty"
    tr = page.total_runs()
    assert tr != "", f"[{model}] Total runs is empty"


# ==================================================================
# 11. Upgrade Job Execution (30 cases: 10 combos × 3 models)
# ==================================================================
UPGRADE_JOB_COMBOS = [
    ("cpe_gateway_v4.0.0.bin", "ci"),
    ("cpe_gateway_v5.0.0.bin", "manual"),
    ("cpe_gateway_v6.0.0.bin", "local"),
    ("cpe_gateway_v7.7.7.bin", "ci"),
    ("cpe_gateway_v8.0.0.bin", "manual"),
    ("cpe_gateway_v9.1.0.bin", "local"),
    ("cpe_gateway_v10.5.0.bin", "ci"),
    ("cpe_gateway_v11.0.0.bin", "manual"),
    ("cpe_gateway_v12.3.1.bin", "ci"),
    ("cpe_gateway_v13.0.0.bin", "local"),
]


@pytest.mark.parametrize("filename,source_type,model", [
    (fn, st, m) for (fn, st) in UPGRADE_JOB_COMBOS for m in PROFILES
])
@allure.feature("UI Regression")
@allure.story("Upgrade Job Execution")
def test_upgrade_job_regression(logged_in_driver, filename, source_type, model):
    """Register artifact and run upgrade job across models and source types."""
    # Register artifact
    art_page = ArtifactsPage(logged_in_driver, BASE_URL, model=model)
    art_page.load()
    art_page.register_artifact(
        filename=filename,
        source_type=source_type,
        source_ref=f"regression-{model}",
        note=f"Regression test for {model}",
    )
    msg = art_page.message()
    assert msg != "", f"[{model}] Expected artifact message for {filename!r}"
    assert "成功" in msg or "success" in msg.lower(), \
        f"[{model}] Artifact registration failed: {msg!r}"

    # Run job
    jobs_page = JobsPage(logged_in_driver, BASE_URL, model=model)
    jobs_page.load()
    jobs_page.run_first_job()
    job_msg = jobs_page.message()
    assert job_msg != "", f"[{model}] Expected job message for {filename!r}"
    assert "完成" in job_msg or "passed" in job_msg.lower() or "成功" in job_msg, \
        f"[{model}] Job failed: {job_msg!r}"