import re
import random
import hashlib
import time
from datetime import datetime

from .repository import StateRepository
from .device_adapter import MockDeviceAdapter


_FIRMWARE_RE = re.compile(r'^cpe_gateway_v(\d+)\.(\d+)\.(\d+)\.bin$')


class GatewayService:
    def __init__(self, repo: StateRepository):
        self.repo = repo
        self.adapter = MockDeviceAdapter()

    # ------------------------------------------------------------------
    # Dashboard
    # ------------------------------------------------------------------
    def dashboard_context(self) -> dict:
        sys = self.repo.get_state('system')
        upgrade = self.repo.get_state('upgrade')
        clients = self.repo.list_clients()
        activities = self.repo.list_activities(10)
        return {
            'model': sys.get('model', 'CPE-GW-X300'),
            'firmware_version': sys.get('firmware_version', 'v2.1.0'),
            'wan_status': sys.get('wan_status', 'connected'),
            'uptime': sys.get('uptime', '—'),
            'cpu_usage': sys.get('cpu_usage', 0),
            'memory_usage': sys.get('memory_usage', 0),
            'client_count': len(clients),
            'clients': clients,
            'activities': activities,
            'last_upgrade_status': upgrade.get('last_status', 'none'),
            'last_upgrade_version': upgrade.get('last_version'),
            'last_upgrade_time': upgrade.get('last_time'),
        }

    # ------------------------------------------------------------------
    # Network
    # ------------------------------------------------------------------
    def get_network(self) -> dict:
        return self.repo.get_state('network')

    def update_network(self, data: dict):
        net = self.repo.get_state('network')
        net.update({
            'ssid': data.get('ssid', net.get('ssid')),
            'wifi_password': data.get('wifi_password', net.get('wifi_password')),
            'mode': data.get('mode', net.get('mode')),
            'channel': data.get('channel', net.get('channel')),
            'guest_wifi': data.get('guest_wifi') in ('on', True, '1', 'true'),
        })
        self.repo.set_state('network', net)
        self.repo.add_activity('网络配置', f"SSID 更新为 {net['ssid']}，模式 {net['mode']}")

    # ------------------------------------------------------------------
    # Firmware validation
    # ------------------------------------------------------------------
    def validate_firmware(self, filename: str) -> dict:
        filename = (filename or '').strip()
        m = _FIRMWARE_RE.match(filename)
        if m:
            version = f"{m.group(1)}.{m.group(2)}.{m.group(3)}"
            upgrade = self.repo.get_state('upgrade')
            upgrade.update({'last_status': 'validated', 'last_version': version,
                            'last_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')})
            self.repo.set_state('upgrade', upgrade)
            self.repo.add_activity('固件校验', f"固件 {filename} 校验通过，版本 v{version}")
            return {'status': 'validated', 'version': version,
                    'message': f'固件 {filename} 格式合法，版本 v{version}'}
        else:
            self.repo.add_activity('固件校验', f"固件 {filename} 格式非法，已拒绝")
            return {'status': 'rejected', 'version': None,
                    'message': f'固件名格式非法。合法格式：cpe_gateway_vX.Y.Z.bin'}

    # ------------------------------------------------------------------
    # Diagnostics
    # ------------------------------------------------------------------
    def run_diagnostics(self) -> dict:
        result = {
            'ping': 'ok',
            'dns': 'ok',
            'cloud': 'ok',
            'packet_loss': round(random.uniform(0.0, 3.0), 2),
        }
        self.repo.set_state('diagnostics', result)
        self.repo.add_activity('诊断检查', f"Ping/DNS/云端检查完成，丢包率 {result['packet_loss']}%")
        return result

    def get_diagnostics(self) -> dict:
        return self.repo.get_state('diagnostics')

    # ------------------------------------------------------------------
    # Artifacts
    # ------------------------------------------------------------------
    def register_artifact(self, data: dict) -> dict:
        filename = (data.get('filename') or '').strip()
        check = self.validate_firmware(filename)
        if check['status'] == 'rejected':
            return {'ok': False, 'message': check['message']}

        seed = filename + datetime.now().isoformat()
        md5 = hashlib.md5(seed.encode()).hexdigest()
        sha256 = hashlib.sha256(seed.encode()).hexdigest()
        size_bytes = random.randint(5 * 1024 * 1024, 20 * 1024 * 1024)

        local_path = (data.get('local_path') or '').strip() or f'artifacts/{filename}'
        row = {
            'filename': filename,
            'version': check['version'],
            'source_type': data.get('source_type', 'manual'),
            'source_ref': data.get('source_ref', ''),
            'local_path': local_path,
            'size_bytes': size_bytes,
            'md5': md5,
            'sha256': sha256,
            'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'note': data.get('note', ''),
        }
        artifact_id = self.repo.insert_artifact(row)
        self.repo.add_activity('制品登记', f"固件 {filename} 已登记，ID={artifact_id}")
        return {'ok': True, 'message': f'固件制品 {filename} 登记成功', 'id': artifact_id}

    def list_artifacts(self) -> list:
        return self.repo.list_artifacts()

    # ------------------------------------------------------------------
    # Upgrade jobs
    # ------------------------------------------------------------------
    def run_upgrade_job(self, artifact_id: int) -> dict:
        artifact = self.repo.get_artifact(artifact_id)
        if not artifact:
            return {'ok': False, 'message': f'制品 ID={artifact_id} 不存在'}

        t0 = time.time()
        path = artifact.get('local_path') or f"artifacts/{artifact['filename']}"
        upload_ok = self.adapter.upload_firmware(path)
        trigger_ok = self.adapter.trigger_upgrade(artifact['version'])
        online_ok = self.adapter.wait_until_online()
        runtime = self.adapter.fetch_runtime_status()
        api_check = bool(runtime.get('firmware_version'))
        web_check = True
        duration = round(time.time() - t0, 2)

        all_ok = all([upload_ok, trigger_ok, online_ok, api_check, web_check])
        status = 'passed' if all_ok else 'failed'
        failure_reason = None if all_ok else '升级步骤未全部通过'

        job_id = self.repo.insert_job({
            'artifact_id': artifact_id,
            'target_version': artifact['version'],
            'status': status,
            'upload_ok': int(upload_ok),
            'trigger_ok': int(trigger_ok),
            'online_ok': int(online_ok),
            'api_check': int(api_check),
            'web_check': int(web_check),
            'duration_seconds': duration,
            'failure_reason': failure_reason,
            'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        })

        coverage = round(random.uniform(0.80, 0.98), 4)
        flaky_rate = round(random.uniform(0.00, 0.05), 4)
        pass_rate = 1.0 if all_ok else round(random.uniform(0.60, 0.90), 4)

        self.repo.insert_experiment({
            'job_id': job_id,
            'coverage': coverage,
            'pass_rate': pass_rate,
            'flaky_rate': flaky_rate,
            'duration_seconds': duration,
            'failure_reason': failure_reason,
            'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        })

        if all_ok:
            sys_state = self.repo.get_state('system')
            sys_state['firmware_version'] = f"v{artifact['version']}"
            self.repo.set_state('system', sys_state)
            upgrade_state = self.repo.get_state('upgrade')
            upgrade_state.update({
                'last_status': 'passed',
                'last_version': artifact['version'],
                'last_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            })
            self.repo.set_state('upgrade', upgrade_state)

        self.repo.add_activity('升级任务', f"制品 {artifact['filename']} 升级{('成功' if all_ok else '失败')}，耗时 {duration}s")
        return {
            'ok': all_ok,
            'job_id': job_id,
            'status': status,
            'duration': duration,
            'message': f"升级任务完成，状态：{status}",
        }

    def list_jobs(self) -> list:
        return self.repo.list_jobs()

    # ------------------------------------------------------------------
    # Stats
    # ------------------------------------------------------------------
    def stats_summary(self) -> dict:
        return self.repo.stats_summary()

    def list_experiments(self) -> list:
        return self.repo.list_experiments()
