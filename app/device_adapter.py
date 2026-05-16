import random
import time
from abc import ABC, abstractmethod


class DeviceAdapter(ABC):
    @abstractmethod
    def upload_firmware(self, path: str) -> bool: ...

    @abstractmethod
    def trigger_upgrade(self, version: str) -> bool: ...

    @abstractmethod
    def wait_until_online(self, timeout_seconds: int = 30) -> bool: ...

    @abstractmethod
    def fetch_runtime_status(self) -> dict: ...

    @abstractmethod
    def validate_firmware_package(self, path: str) -> bool: ...

    @abstractmethod
    def reboot_device(self) -> bool: ...


class MockDeviceAdapter(DeviceAdapter):
    def __init__(self, failure_rate=0.0):
        self._failure_rate = failure_rate
        self._current_version = "2.1.0"  # default mock firmware version

    def upload_firmware(self, path: str) -> bool:
        time.sleep(0.4)
        if not path:
            return False
        return True  # mock mode: no real file required

    def validate_firmware_package(self, path: str) -> bool:
        time.sleep(0.3)
        return bool(path)

    def trigger_upgrade(self, version: str) -> bool:
        time.sleep(0.3)
        if not version:
            return False
        if random.random() < self._failure_rate:
            return False  # 模拟故障注入
        # Normalize: 如果 version 以 'v' 开头则去掉，再统一加 'v' 前缀
        normalized = version.lstrip("v")
        self._current_version = normalized
        return True

    def reboot_device(self) -> bool:
        time.sleep(1.0)
        if random.random() < self._failure_rate:
            return False  # 模拟故障注入
        return True

    def wait_until_online(self, timeout_seconds: int = 30) -> bool:
        time.sleep(0.8)
        if random.random() < self._failure_rate:
            return False  # 模拟故障注入
        return True

    def fetch_runtime_status(self) -> dict:
        return {
            'firmware_version': f"v{self._current_version}",
            'wan_status': 'connected',
            'cpu_usage': random.randint(15, 45),
            'memory_usage': random.randint(40, 70),
        }


# ------------------------------------------------------------------
# Reserved adapters — real-device extensions (not implemented)
# ------------------------------------------------------------------

class HttpDeviceAdapter(DeviceAdapter):
    """Connects to a real CPE via its HTTP management API."""

    def upload_firmware(self, path: str) -> bool:
        raise NotImplementedError

    def trigger_upgrade(self, version: str) -> bool:
        raise NotImplementedError

    def wait_until_online(self, timeout_seconds: int = 30) -> bool:
        raise NotImplementedError

    def fetch_runtime_status(self) -> dict:
        raise NotImplementedError

    def validate_firmware_package(self, path: str) -> bool:
        raise NotImplementedError("该适配器暂未实现固件包校验功能")

    def reboot_device(self) -> bool:
        raise NotImplementedError("该适配器暂未实现设备重启功能")


class SshDeviceAdapter(DeviceAdapter):
    """Connects to a real CPE via SSH shell commands."""

    def upload_firmware(self, path: str) -> bool:
        raise NotImplementedError

    def trigger_upgrade(self, version: str) -> bool:
        raise NotImplementedError

    def wait_until_online(self, timeout_seconds: int = 30) -> bool:
        raise NotImplementedError

    def fetch_runtime_status(self) -> dict:
        raise NotImplementedError

    def validate_firmware_package(self, path: str) -> bool:
        raise NotImplementedError("该适配器暂未实现固件包校验功能")

    def reboot_device(self) -> bool:
        raise NotImplementedError("该适配器暂未实现设备重启功能")


class TelnetDeviceAdapter(DeviceAdapter):
    """Connects to a real CPE via Telnet (legacy devices)."""

    def upload_firmware(self, path: str) -> bool:
        raise NotImplementedError

    def trigger_upgrade(self, version: str) -> bool:
        raise NotImplementedError

    def wait_until_online(self, timeout_seconds: int = 30) -> bool:
        raise NotImplementedError

    def fetch_runtime_status(self) -> dict:
        raise NotImplementedError

    def validate_firmware_package(self, path: str) -> bool:
        raise NotImplementedError("该适配器暂未实现固件包校验功能")

    def reboot_device(self) -> bool:
        raise NotImplementedError("该适配器暂未实现设备重启功能")


class SerialDeviceAdapter(DeviceAdapter):
    """Connects to a real CPE via serial/UART console."""

    def upload_firmware(self, path: str) -> bool:
        raise NotImplementedError

    def trigger_upgrade(self, version: str) -> bool:
        raise NotImplementedError

    def wait_until_online(self, timeout_seconds: int = 30) -> bool:
        raise NotImplementedError

    def fetch_runtime_status(self) -> dict:
        raise NotImplementedError

    def validate_firmware_package(self, path: str) -> bool:
        raise NotImplementedError("该适配器暂未实现固件包校验功能")

    def reboot_device(self) -> bool:
        raise NotImplementedError("该适配器暂未实现设备重启功能")
