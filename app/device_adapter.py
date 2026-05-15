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


class MockDeviceAdapter(DeviceAdapter):
    def upload_firmware(self, path: str) -> bool:
        time.sleep(0.4)
        if not path:
            return False
        return True  # mock mode: no real file required

    def trigger_upgrade(self, version: str) -> bool:
        time.sleep(0.3)
        return bool(version)

    def wait_until_online(self, timeout_seconds: int = 30) -> bool:
        time.sleep(0.8)
        return True

    def fetch_runtime_status(self) -> dict:
        return {
            'firmware_version': 'v2.1.0',
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
