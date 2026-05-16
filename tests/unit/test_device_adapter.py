"""Unit tests for MockDeviceAdapter — no real device, no browser."""
import os
import sys
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from app.device_adapter import MockDeviceAdapter


def test_mock_upload_firmware_success():
    adapter = MockDeviceAdapter()
    assert adapter.upload_firmware("artifacts/cpe_gateway_v2.1.0.bin") is True


def test_mock_upload_firmware_empty_path_fails():
    adapter = MockDeviceAdapter()
    assert adapter.upload_firmware("") is False


def test_mock_trigger_upgrade_success():
    adapter = MockDeviceAdapter()
    assert adapter.trigger_upgrade("2.1.0") is True


def test_mock_trigger_upgrade_empty_version_fails():
    adapter = MockDeviceAdapter()
    assert adapter.trigger_upgrade("") is False


def test_mock_wait_until_online():
    adapter = MockDeviceAdapter()
    assert adapter.wait_until_online() is True


def test_mock_wait_until_online_custom_timeout():
    adapter = MockDeviceAdapter()
    assert adapter.wait_until_online(timeout_seconds=5) is True


def test_mock_fetch_runtime_status():
    adapter = MockDeviceAdapter()
    status = adapter.fetch_runtime_status()
    assert "firmware_version" in status
    assert "wan_status" in status
    assert "cpu_usage" in status
    assert "memory_usage" in status
    assert status["wan_status"] == "connected"
    assert 15 <= status["cpu_usage"] <= 45
    assert 40 <= status["memory_usage"] <= 70


def test_mock_reboot_device_success():
    adapter = MockDeviceAdapter()
    assert adapter.reboot_device() is True


def test_mock_validate_firmware_package_success():
    adapter = MockDeviceAdapter()
    assert adapter.validate_firmware_package("artifacts/cpe_gateway_v2.1.0.bin") is True


def test_mock_validate_firmware_package_empty_path_fails():
    adapter = MockDeviceAdapter()
    assert adapter.validate_firmware_package("") is False


# ------------------------------------------------------------------
# P0-2: trigger_upgrade should update internal version state
# ------------------------------------------------------------------
def test_trigger_upgrade_sets_runtime_version_with_v_prefix():
    adapter = MockDeviceAdapter()
    adapter.trigger_upgrade("v6.0.0")
    status = adapter.fetch_runtime_status()
    assert status["firmware_version"] == "v6.0.0"


def test_trigger_upgrade_sets_runtime_version_without_v_prefix():
    adapter = MockDeviceAdapter()
    adapter.trigger_upgrade("6.0.0")
    status = adapter.fetch_runtime_status()
    assert status["firmware_version"] == "v6.0.0"


def test_runtime_version_defaults_to_v2_1_0():
    adapter = MockDeviceAdapter()
    status = adapter.fetch_runtime_status()
    assert status["firmware_version"] == "v2.1.0"


# ------------------------------------------------------------------
# P0-1: Reserved adapters can be instantiated without TypeError
# ------------------------------------------------------------------
def test_http_adapter_can_be_instantiated():
    from app.device_adapter import HttpDeviceAdapter
    adapter = HttpDeviceAdapter()
    assert isinstance(adapter, HttpDeviceAdapter)


def test_ssh_adapter_can_be_instantiated():
    from app.device_adapter import SshDeviceAdapter
    adapter = SshDeviceAdapter()
    assert isinstance(adapter, SshDeviceAdapter)


def test_telnet_adapter_can_be_instantiated():
    from app.device_adapter import TelnetDeviceAdapter
    adapter = TelnetDeviceAdapter()
    assert isinstance(adapter, TelnetDeviceAdapter)


def test_serial_adapter_can_be_instantiated():
    from app.device_adapter import SerialDeviceAdapter
    adapter = SerialDeviceAdapter()
    assert isinstance(adapter, SerialDeviceAdapter)


# ------------------------------------------------------------------
# P0-3: Reserved adapter methods raise NotImplementedError
# ------------------------------------------------------------------
_RESERVED_ADAPTERS = [
    ('HttpDeviceAdapter',  'HttpDeviceAdapter'),
    ('SshDeviceAdapter',   'SshDeviceAdapter'),
    ('TelnetDeviceAdapter','TelnetDeviceAdapter'),
    ('SerialDeviceAdapter','SerialDeviceAdapter'),
]

_ADAPTER_METHODS = [
    ('upload_firmware', ('artifacts/fw.bin',)),
    ('trigger_upgrade', ('1.0.0',)),
    ('wait_until_online', (30,)),
    ('fetch_runtime_status', ()),
    ('validate_firmware_package', ('artifacts/fw.bin',)),
    ('reboot_device', ()),
]


@pytest.mark.parametrize('class_name,import_cls_name', _RESERVED_ADAPTERS)
@pytest.mark.parametrize('method_name, args', _ADAPTER_METHODS)
def test_reserved_adapter_methods_raise_not_implemented(class_name, import_cls_name, method_name, args):
    import importlib
    mod = importlib.import_module('app.device_adapter')
    cls = getattr(mod, import_cls_name)
    adapter = cls()
    method = getattr(adapter, method_name)
    with pytest.raises(NotImplementedError):
        method(*args)