"""Unit tests for GatewayService — no browser, no real CPE."""
import pytest
import tempfile
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from app.repository import StateRepository
from app.service import GatewayService


@pytest.fixture
def svc(tmp_path):
    db = str(tmp_path / "test.db")
    repo = StateRepository(db)
    repo.init_db()
    return GatewayService(repo)


# ------------------------------------------------------------------
# validate_firmware
# ------------------------------------------------------------------
def test_valid_firmware_name_is_accepted(svc):
    r = svc.validate_firmware("cpe_gateway_v2.1.0.bin")
    assert r["status"] == "validated"
    assert r["version"] == "2.1.0"


def test_invalid_firmware_extension_is_rejected(svc):
    r = svc.validate_firmware("cpe_gateway_v2.1.0.zip")
    assert r["status"] == "rejected"
    assert r["version"] is None


def test_invalid_firmware_pattern_is_rejected(svc):
    for bad in ["firmware.bin", "cpe_gateway_v2.1.bin", "cpe_gateway_vA.B.C.bin", ""]:
        r = svc.validate_firmware(bad)
        assert r["status"] == "rejected", f"Expected rejected for: {bad!r}"


# ------------------------------------------------------------------
# network
# ------------------------------------------------------------------
def test_network_config_can_be_saved(svc):
    svc.update_network({"ssid": "TestNet", "mode": "static", "channel": "11"})
    net = svc.get_network()
    assert net["ssid"] == "TestNet"
    assert net["mode"] == "static"
    assert net["channel"] == "11"


# ------------------------------------------------------------------
# diagnostics
# ------------------------------------------------------------------
def test_diagnostics_can_be_refreshed(svc):
    result = svc.run_diagnostics()
    assert result["ping"] == "ok"
    assert result["dns"] == "ok"
    assert result["cloud"] == "ok"
    assert 0.0 <= result["packet_loss"] <= 3.0


# ------------------------------------------------------------------
# artifacts
# ------------------------------------------------------------------
def test_register_artifact_creates_record(svc):
    res = svc.register_artifact({
        "filename": "cpe_gateway_v3.0.0.bin",
        "source_type": "manual",
        "source_ref": "build-42",
        "note": "test artifact",
    })
    assert res["ok"] is True
    assert "id" in res
    artifacts = svc.list_artifacts()
    assert any(a["filename"] == "cpe_gateway_v3.0.0.bin" for a in artifacts)


def test_invalid_artifact_is_rejected(svc):
    res = svc.register_artifact({"filename": "bad_firmware.exe"})
    assert res["ok"] is False


# ------------------------------------------------------------------
# upgrade job
# ------------------------------------------------------------------
def test_run_upgrade_job_passes_with_mock_adapter(svc):
    svc.register_artifact({"filename": "cpe_gateway_v4.0.0.bin", "source_type": "ci"})
    artifacts = svc.list_artifacts()
    artifact_id = artifacts[0]["id"]
    result = svc.run_upgrade_job(artifact_id)
    assert result["ok"] is True
    assert result["status"] == "passed"
    assert result["job_id"] > 0


# ------------------------------------------------------------------
# stats
# ------------------------------------------------------------------
def test_stats_summary_returns_metrics(svc):
    svc.register_artifact({"filename": "cpe_gateway_v5.0.0.bin"})
    artifacts = svc.list_artifacts()
    svc.run_upgrade_job(artifacts[0]["id"])
    summary = svc.stats_summary()
    assert "total" in summary
    assert "passed" in summary
    assert "pass_rate" in summary
    assert "coverage" in summary
    assert "flaky_rate" in summary
    assert "avg_duration" in summary
    assert summary["total"] >= 1


# ------------------------------------------------------------------
# P0-2: api_check should validate runtime firmware_version
# ------------------------------------------------------------------
def test_run_upgrade_job_api_check_equals_1_when_version_matches(svc):
    """合法固件升级后，api_check 应为 1"""
    svc.register_artifact({"filename": "cpe_gateway_v4.0.0.bin"})
    artifacts = svc.list_artifacts()
    result = svc.run_upgrade_job(artifacts[0]["id"])
    assert result["ok"] is True
    assert result["status"] == "passed"
    assert result["steps"]["api_check"] == 1


def test_run_upgrade_job_fails_when_runtime_version_mismatch(svc, monkeypatch):
    """模拟运行时固件版本与目标版本不一致时，api_check 为 0，任务 FAILED"""
    svc.register_artifact({"filename": "cpe_gateway_v4.0.0.bin"})
    artifacts = svc.list_artifacts()
    # 在 trigger_upgrade 正常执行后，patch fetch_runtime_status 返回不匹配版本
    original_fetch = svc.adapter.fetch_runtime_status

    def mismatched_runtime():
        r = original_fetch()
        r["firmware_version"] = "v3.0.0"
        return r

    monkeypatch.setattr(svc.adapter, "fetch_runtime_status", mismatched_runtime)
    result = svc.run_upgrade_job(artifacts[0]["id"])
    assert result["ok"] is False
    assert result["status"] == "failed"
    assert result["steps"]["api_check"] == 0
    assert "运行版本与目标版本不一致" in (result["failure_reason"] or "")
