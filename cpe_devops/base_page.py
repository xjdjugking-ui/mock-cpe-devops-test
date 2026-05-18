"""Base page object — shared driver helpers."""
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

# ------------------------------------------------------------------
# 多型号设备配置映射（极简 Mock 方案）
# 同一套前端，不同型号元素 ID 不同 → 验证零脚本适配
# ------------------------------------------------------------------
DEVICE_PROFILES = {
    "cpe_gw_x300": {
        "model": "cpe_gw_x300",
        "display": "CPE-GW-X300 桌面型千兆网关",
        "management": "http",
        "firmware_pattern": "cpe_gateway_v*.*.*.bin",
        "selectors": {
            "username": "username",
            "password": "password",
            "login_button": "login-button",
            # 网络设置 — 当前模板元素 ID（各型号不同则修改此处）
            "ssid": "ssid",
            "wifi_password": "wifi-password",
            "mode": "mode",
            "channel": "channel",
            "guest_wifi": "guest-wifi",
            "save_network_button": "save-network-button",
            # 固件升级
            "firmware_filename": "firmware-filename",
            "firmware_submit": "validate-firmware-button",
            # 制品管理
            "artifact_filename": "artifact-filename",
            "artifact_source_type": "artifact-source-type",
            "artifact_source_ref": "artifact-source-ref",
            "artifact_local_path": "artifact-path",
            "artifact_note": "artifact-note",
            "artifact_submit": "register-artifact-button",
            # 作业
            "artifact_select": "artifact-select",
            "run_job_button": "run-upgrade-job-button",
        },
    },
    # --------------- 以下两个型号的 selector 值与 X300 完全相同 ---------------
    # Mock 阶段共用同一套 HTML → 验证"POM 不硬编码 ID"的架构可行性
    # 真机阶段只需修改此文件中的 selector 映射，测试脚本 0 改动
    "cpe_gw_x500": {
        "model": "cpe_gw_x500",
        "display": "CPE-GW-X500 高性能双频网关",
        "management": "ssh",
        "firmware_pattern": "cpe_gateway_v*.*.*.bin",
        "selectors": {
            "username": "username",
            "password": "password",
            "login_button": "login-button",
            "ssid": "ssid",
            "wifi_password": "wifi-password",
            "mode": "mode",
            "channel": "channel",
            "guest_wifi": "guest-wifi",
            "save_network_button": "save-network-button",
            "firmware_filename": "firmware-filename",
            "firmware_submit": "validate-firmware-button",
            "artifact_filename": "artifact-filename",
            "artifact_source_type": "artifact-source-type",
            "artifact_source_ref": "artifact-source-ref",
            "artifact_local_path": "artifact-path",
            "artifact_note": "artifact-note",
            "artifact_submit": "register-artifact-button",
            "artifact_select": "artifact-select",
            "run_job_button": "run-upgrade-job-button",
        },
    },
    "mifi_m3": {
        "model": "mifi_m3",
        "display": "MiFi-M3 随身移动热点",
        "management": "serial",
        "firmware_pattern": "mifi_firmware_*.*.*.img",
        "selectors": {
            "username": "username",
            "password": "password",
            "login_button": "login-button",
            "ssid": "ssid",
            "wifi_password": "wifi-password",
            "mode": "mode",
            "channel": "channel",
            "guest_wifi": "guest-wifi",
            "save_network_button": "save-network-button",
            "firmware_filename": "firmware-filename",
            "firmware_submit": "validate-firmware-button",
            "artifact_filename": "artifact-filename",
            "artifact_source_type": "artifact-source-type",
            "artifact_source_ref": "artifact-source-ref",
            "artifact_local_path": "artifact-path",
            "artifact_note": "artifact-note",
            "artifact_submit": "register-artifact-button",
            "artifact_select": "artifact-select",
            "run_job_button": "run-upgrade-job-button",
        },
    },
}


def load_device_profile(name: str = "cpe_gw_x300") -> dict:
    """加载设备型号配置，默认返回 cpe_gw_x300 桌面型 CPE。"""
    return DEVICE_PROFILES.get(name, DEVICE_PROFILES["cpe_gw_x300"])


# ------------------------------------------------------------------
# Adapt 映射：将前端的?"model=?" 参数注入到渲染上下文
# ------------------------------------------------------------------
MODEL_OVERRIDES = {
    "cpe_gw_x300": {"model": "cpe_gw_x300", "display": "CPE-GW-X300"},
    "cpe_gw_x500": {"model": "cpe_gw_x500", "display": "CPE-GW-X500"},
    "mifi_m3": {"model": "mifi_m3", "display": "MiFi-M3"},
}


class BasePage:
    def __init__(self, driver, base_url: str = "http://127.0.0.1:5000", model: str = "cpe_gw_x300"):
        self.driver = driver
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.profile = load_device_profile(model)
        self.sel = self.profile["selectors"]

    def _url(self, path: str) -> str:
        return self.base_url + path

    def _wait(self, timeout: int = 20):
        return WebDriverWait(self.driver, timeout)

    def _find(self, by, value, timeout: int = 20):
        return self._wait(timeout).until(EC.presence_of_element_located((by, value)))

    def _find_visible(self, by, value, timeout: int = 20):
        return self._wait(timeout).until(EC.visibility_of_element_located((by, value)))

    def _click(self, element_id: str):
        self._find(By.ID, element_id).click()

    def _fill(self, element_id: str, value: str):
        el = self._find(By.ID, element_id)
        el.clear()
        el.send_keys(value)

    def _text(self, element_id: str) -> str:
        return self._find_visible(By.ID, element_id).text.strip()

    def _select_by_value(self, element_id: str, value: str):
        from selenium.webdriver.support.ui import Select
        Select(self._find(By.ID, element_id)).select_by_value(value)