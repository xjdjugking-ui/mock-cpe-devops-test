"""Unit tests for StateRepository — uses a temp SQLite DB."""
import pytest
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from app.repository import StateRepository


@pytest.fixture
def repo(tmp_path):
    db = str(tmp_path / "test.db")
    r = StateRepository(db)
    r.init_db()
    return r


# ------------------------------------------------------------------
# Schema
# ------------------------------------------------------------------
def test_database_tables_are_created(repo):
    import sqlite3
    conn = sqlite3.connect(repo.db_path)
    tables = {row[0] for row in conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table'"
    ).fetchall()}
    conn.close()
    expected = {"singleton_state", "clients", "activities",
                "firmware_artifacts", "upgrade_jobs", "experiment_runs"}
    assert expected.issubset(tables)


# ------------------------------------------------------------------
# singleton_state
# ------------------------------------------------------------------
def test_singleton_state_can_be_saved_and_loaded(repo):
    repo.set_state("test_section", {"key": "value", "num": 42})
    loaded = repo.get_state("test_section")
    assert loaded["key"] == "value"
    assert loaded["num"] == 42


# ------------------------------------------------------------------
# activities
# ------------------------------------------------------------------
def test_activity_can_be_added(repo):
    before = len(repo.list_activities())
    repo.add_activity("测试事件", "这是一条测试活动记录")
    after = repo.list_activities()
    assert len(after) == before + 1
    assert any(a["event"] == "测试事件" for a in after)


# ------------------------------------------------------------------
# firmware_artifacts
# ------------------------------------------------------------------
def test_artifact_can_be_inserted_and_listed(repo):
    data = {
        "filename": "cpe_gateway_v1.0.0.bin",
        "version": "1.0.0",
        "source_type": "manual",
        "source_ref": "test-ref",
        "local_path": "artifacts/cpe_gateway_v1.0.0.bin",
        "size_bytes": 10485760,
        "md5": "abc123",
        "sha256": "def456",
        "created_at": "2024-01-01 00:00:00",
        "note": "unit test artifact",
    }
    artifact_id = repo.insert_artifact(data)
    assert artifact_id > 0
    artifacts = repo.list_artifacts()
    assert any(a["filename"] == "cpe_gateway_v1.0.0.bin" for a in artifacts)
    fetched = repo.get_artifact(artifact_id)
    assert fetched is not None
    assert fetched["version"] == "1.0.0"


# ------------------------------------------------------------------
# upgrade_jobs
# ------------------------------------------------------------------
def test_upgrade_job_can_be_inserted_and_listed(repo):
    job_data = {
        "artifact_id": 1,
        "target_version": "1.0.0",
        "status": "passed",
        "upload_ok": 1,
        "trigger_ok": 1,
        "online_ok": 1,
        "api_check": 1,
        "web_check": 1,
        "duration_seconds": 1.5,
        "failure_reason": None,
        "created_at": "2024-01-01 00:00:00",
    }
    job_id = repo.insert_job(job_data)
    assert job_id > 0
    jobs = repo.list_jobs()
    assert any(j["id"] == job_id for j in jobs)
    assert any(j["status"] == "passed" for j in jobs)


# ------------------------------------------------------------------
# experiment_runs
# ------------------------------------------------------------------
def test_experiment_run_can_be_inserted_and_listed(repo):
    exp_data = {
        "job_id": 1,
        "coverage": 0.92,
        "pass_rate": 1.0,
        "flaky_rate": 0.02,
        "duration_seconds": 1.5,
        "failure_reason": None,
        "created_at": "2024-01-01 00:00:00",
    }
    exp_id = repo.insert_experiment(exp_data)
    assert exp_id > 0
    exps = repo.list_experiments()
    assert any(e["id"] == exp_id for e in exps)
    assert any(abs(e["coverage"] - 0.92) < 0.001 for e in exps)
