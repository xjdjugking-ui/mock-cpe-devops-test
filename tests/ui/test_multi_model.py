"""多型号适配验证 — 同一套脚本 x 3 个设备型号

验证"零脚本适配"：POM 通过 device profile 映射不同元素 ID，
测试脚本完全不变，仅 parametrize 切换型号。
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

# 三个核心型号 → parametrize 自动生成 3 倍用例数
PROFILES = ["cpe_gw_x300", "cpe_gw_x500", "mifi_m3"]


@pytest.mark.parametrize("model", PROFILES)
@allure.feature("Multi-Model Adaptation")
@allure.story("Login Across Models")
def test_login_across_models(driver, model):
    """验证登录页在不同型号下正常工作（ID 映射来自 profile）"""
    page = LoginPage(driver, BASE_URL, model=model)
    page.load()
    page.login("admin", "admin123")
    from selenium.webdriver.support.ui import WebDriverWait
    WebDriverWait(driver, 10).until(lambda d: "/dashboard" in d.current_url)
    assert "/dashboard" in driver.current_url


@pytest.mark.parametrize("model", PROFILES)
@allure.feature("Multi-Model Adaptation")
@allure.story("Network Config Across Models")
def test_network_config_across_models(logged_in_driver, model):
    """验证网络设置在不同型号下使用不同元素 ID 仍能正确操作"""
    page = NetworkPage(logged_in_driver, BASE_URL, model=model)
    page.load()
    page.save_network(
        ssid=f"Net-{model[-3:]}",
        password="testpass123",
        mode="dhcp",
        channel="6",
        guest_enabled=False,
    )
    msg = page.message()
    assert msg != "", f"[{model}] Expected a message but got empty string"
    assert "保存" in msg or "saved" in msg.lower(), \
        f"[{model}] Unexpected message: {msg!r}"


@pytest.mark.parametrize("model", PROFILES)
@allure.feature("Multi-Model Adaptation")
@allure.story("Firmware Validation Across Models")
def test_firmware_validation_across_models(logged_in_driver, model):
    """验证固件验证在不同型号下仍能正确工作"""
    page = UpgradePage(logged_in_driver, BASE_URL, model=model)
    page.load()
    page.validate_firmware("cpe_gateway_v3.0.0.bin")
    msg = page.message()
    assert msg != "", f"[{model}] Expected validation message but got empty string"
    assert "validated" in msg.lower() or "通过" in msg or "合法" in msg, \
        f"[{model}] Unexpected message: {msg!r}"


@pytest.mark.parametrize("model", PROFILES)
@allure.feature("Multi-Model Adaptation")
@allure.story("Artifact Registration Across Models")
def test_artifact_registration_across_models(logged_in_driver, model):
    """验证固件制品注册在不同型号下仍能正确工作"""
    page = ArtifactsPage(logged_in_driver, BASE_URL, model=model)
    page.load()
    page.register_artifact(
        filename=f"{model}_v7.0.0.bin",
        source_type="manual",
        source_ref=f"{model}-build",
        path=f"artifacts/{model}_v7.0.0.bin",
        note=f"Multi-model test for {model}",
    )
    msg = page.message()
    assert msg != "", f"[{model}] Expected artifact registration message but got empty string"
    assert "成功" in msg or "success" in msg.lower(), \
        f"[{model}] Unexpected message: {msg!r}"


@pytest.mark.parametrize("model", PROFILES)
@allure.feature("Multi-Model Adaptation")
@allure.story("Upgrade Job Across Models")
def test_upgrade_job_across_models(logged_in_driver, model):
    """验证升级作业在不同型号下仍能正确执行"""
    art_page = ArtifactsPage(logged_in_driver, BASE_URL, model=model)
    art_page.load()
    art_page.register_artifact(
        filename=f"{model}_v6.0.0.bin",
        source_type="ci",
        source_ref=f"{model}-job-build",
    )
    jobs_page = JobsPage(logged_in_driver, BASE_URL, model=model)
    jobs_page.load()
    jobs_page.run_first_job()
    msg = jobs_page.message()
    assert msg != "", f"[{model}] Expected job completion message but got empty string"
    assert "完成" in msg or "passed" in msg.lower() or "成功" in msg, \
        f"[{model}] Unexpected message: {msg!r}"