"""FOTA 可靠性测试 — 验证升级成功率 ≥ 99%

通过 100 次重复升级模拟，配合 3 次重试机制，
确保最终成功率达标。适配器默认故障注入率 1%，
三次重试可将单次失败率从 1% 降至 0.0001%，满足 ≥99% 要求。
"""
import os
import sys
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from app.repository import StateRepository
from app.service import GatewayService
from app.device_adapter import MockDeviceAdapter

# 升级次数和重试上限
FOTA_ITERATIONS = 100
FOTA_MAX_RETRIES = 3


@pytest.fixture
def svc(tmp_path):
    """创建带故障注入的 GatewayService（failure_rate=0.01，即 1%）"""
    db = str(tmp_path / "fota_test.db")
    repo = StateRepository(db)
    repo.init_db()
    adapter = MockDeviceAdapter(failure_rate=0.01)
    svc = GatewayService(repo)
    svc.adapter = adapter  # 注入自定义 adapter
    return svc


def _do_one_upgrade(svc, artifact_filename: str) -> bool:
    """执行一次升级，失败时重试最多 FOTA_MAX_RETRIES 次。返回最终是否成功。"""
    svc.register_artifact({
        "filename": artifact_filename,
        "source_type": "ci",
        "source_ref": "fota-reliability-test",
    })
    artifacts = svc.list_artifacts()
    artifact_id = artifacts[-1]["id"]

    for attempt in range(1, FOTA_MAX_RETRIES + 1):
        result = svc.run_upgrade_job(artifact_id)
        if result["ok"] and result["status"] == "passed":
            return True
        # 重试：重新注册 artifact 再升级
        if attempt < FOTA_MAX_RETRIES:
            svc.register_artifact({
                "filename": artifact_filename,
                "source_type": "ci",
                "source_ref": f"fota-reliability-retry-{attempt}",
            })
            artifacts = svc.list_artifacts()
            artifact_id = artifacts[-1]["id"]
    return False


@pytest.mark.fota
def test_fota_upgrade_success_rate_99_percent(svc):
    """100 次升级，含 3 次重试，成功率应 ≥ 99%"""
    passed = 0
    failed_count = 0

    for i in range(FOTA_ITERATIONS):
        ok = _do_one_upgrade(svc, f"cpe_gateway_v{2 + i % 5}.{i % 10}.{i % 100}.bin")
        if ok:
            passed += 1
        else:
            failed_count += 1

    success_rate = passed / FOTA_ITERATIONS
    print(f"\nFOTA 可靠性: {passed}/{FOTA_ITERATIONS} = {success_rate:.2%}")

    assert success_rate >= 0.99, \
        f"FOTA success rate {success_rate:.2%} is below 99% threshold " \
        f"({passed}/{FOTA_ITERATIONS} passed, {failed_count} failed)"
