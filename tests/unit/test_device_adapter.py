"""Unit tests for MockDeviceAdapter — no real device, no browser."""
import os
import sys

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
