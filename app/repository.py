from __future__ import annotations
import sqlite3
import json
import os
from datetime import datetime


class StateRepository:
    def __init__(self, db_path: str):
        self.db_path = db_path
        os.makedirs(os.path.dirname(db_path), exist_ok=True)

    def _conn(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    # ------------------------------------------------------------------
    # Schema
    # ------------------------------------------------------------------
    def init_db(self):
        with self._conn() as conn:
            conn.execute("PRAGMA journal_mode=WAL")
            conn.execute("PRAGMA foreign_keys=ON")
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS singleton_state (
                    section    TEXT PRIMARY KEY,
                    payload    TEXT,
                    updated_at TEXT
                );

                CREATE TABLE IF NOT EXISTS clients (
                    id      INTEGER PRIMARY KEY AUTOINCREMENT,
                    name    TEXT,
                    ip      TEXT,
                    band    TEXT,
                    quality INTEGER
                );

                CREATE TABLE IF NOT EXISTS activities (
                    id     INTEGER PRIMARY KEY AUTOINCREMENT,
                    time   TEXT,
                    event  TEXT,
                    detail TEXT
                );

                CREATE TABLE IF NOT EXISTS firmware_artifacts (
                    id          INTEGER PRIMARY KEY AUTOINCREMENT,
                    filename    TEXT,
                    version     TEXT,
                    source_type TEXT,
                    source_ref  TEXT,
                    local_path  TEXT,
                    size_bytes  INTEGER,
                    md5         TEXT,
                    sha256      TEXT,
                    created_at  TEXT,
                    note        TEXT
                );

                CREATE TABLE IF NOT EXISTS upgrade_jobs (
                    id               INTEGER PRIMARY KEY AUTOINCREMENT,
                    artifact_id      INTEGER,
                    target_version   TEXT,
                    status           TEXT,
                    upload_ok        INTEGER,
                    validate_ok      INTEGER DEFAULT 0,
                    trigger_ok       INTEGER,
                    reboot_ok        INTEGER DEFAULT 0,
                    online_ok        INTEGER,
                    api_check        INTEGER,
                    web_check        INTEGER,
                    duration_seconds REAL,
                    failure_reason   TEXT,
                    created_at       TEXT
                );

                CREATE TABLE IF NOT EXISTS experiment_runs (
                    id               INTEGER PRIMARY KEY AUTOINCREMENT,
                    job_id           INTEGER,
                    coverage         REAL,
                    pass_rate        REAL,
                    flaky_rate       REAL,
                    duration_seconds REAL,
                    failure_reason   TEXT,
                    created_at       TEXT
                );
            """)
        self._seed()

    # ------------------------------------------------------------------
    # Seed
    # ------------------------------------------------------------------
    def _seed(self):
        with self._conn() as conn:
            # singleton_state defaults
            defaults = {
                'network': {
                    'ssid': 'CPE-Gateway-5G',
                    'wifi_password': 'cpe@2024',
                    'mode': 'dhcp',
                    'channel': '6',
                    'guest_wifi': False,
                },
                'system': {
                    'model': 'CPE-GW-X300',
                    'firmware_version': 'v2.1.0',
                    'wan_status': 'connected',
                    'uptime': '3d 14h 22m',
                    'cpu_usage': 28,
                    'memory_usage': 54,
                },
                'upgrade': {
                    'last_status': 'none',
                    'last_version': None,
                    'last_time': None,
                },
                'diagnostics': {
                    'ping': 'ok',
                    'dns': 'ok',
                    'cloud': 'ok',
                    'packet_loss': 0.5,
                },
            }
            now = datetime.now().isoformat()
            for section, payload in defaults.items():
                conn.execute(
                    "INSERT OR IGNORE INTO singleton_state(section, payload, updated_at) VALUES(?,?,?)",
                    (section, json.dumps(payload), now),
                )

            # clients
            if conn.execute("SELECT COUNT(*) FROM clients").fetchone()[0] == 0:
                clients = [
                    ('iPhone-14-Pro',  '192.168.1.101', '5GHz', 92),
                    ('MacBook-Air',    '192.168.1.102', '5GHz', 88),
                    ('Android-Tablet', '192.168.1.103', '2.4GHz', 75),
                    ('Smart-TV',       '192.168.1.104', '2.4GHz', 70),
                    ('Laptop-Win11',   '192.168.1.105', '5GHz', 95),
                ]
                conn.executemany(
                    "INSERT INTO clients(name, ip, band, quality) VALUES(?,?,?,?)",
                    clients,
                )

            # activities
            if conn.execute("SELECT COUNT(*) FROM activities").fetchone()[0] == 0:
                acts = [
                    ('系统启动', '设备完成初始化，固件版本 v2.1.0'),
                    ('WAN 连接', 'WAN 口已连接，IP 获取成功'),
                    ('终端接入', 'iPhone-14-Pro 接入 5GHz 频段'),
                    ('终端接入', 'MacBook-Air 接入 5GHz 频段'),
                    ('网络配置', 'SSID 更新为 CPE-Gateway-5G'),
                    ('诊断检查', 'Ping/DNS/云端连通性检查通过'),
                ]
                now2 = datetime.now().isoformat()
                conn.executemany(
                    "INSERT INTO activities(time, event, detail) VALUES(?,?,?)",
                    [(now2, e, d) for e, d in acts],
                )

    # ------------------------------------------------------------------
    # singleton_state helpers
    # ------------------------------------------------------------------
    def get_state(self, section: str) -> dict:
        with self._conn() as conn:
            row = conn.execute(
                "SELECT payload FROM singleton_state WHERE section=?", (section,)
            ).fetchone()
        return json.loads(row['payload']) if row else {}

    def set_state(self, section: str, payload: dict):
        now = datetime.now().isoformat()
        with self._conn() as conn:
            conn.execute(
                "INSERT OR REPLACE INTO singleton_state(section, payload, updated_at) VALUES(?,?,?)",
                (section, json.dumps(payload), now),
            )

    # ------------------------------------------------------------------
    # clients
    # ------------------------------------------------------------------
    def list_clients(self) -> list:
        with self._conn() as conn:
            rows = conn.execute("SELECT * FROM clients ORDER BY id").fetchall()
        return [dict(r) for r in rows]

    # ------------------------------------------------------------------
    # activities
    # ------------------------------------------------------------------
    def add_activity(self, event: str, detail: str):
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        with self._conn() as conn:
            conn.execute(
                "INSERT INTO activities(time, event, detail) VALUES(?,?,?)",
                (now, event, detail),
            )

    def list_activities(self, limit: int = 20) -> list:
        with self._conn() as conn:
            rows = conn.execute(
                "SELECT * FROM activities ORDER BY id DESC LIMIT ?", (limit,)
            ).fetchall()
        return [dict(r) for r in rows]

    # ------------------------------------------------------------------
    # firmware_artifacts
    # ------------------------------------------------------------------
    def insert_artifact(self, data: dict) -> int:
        with self._conn() as conn:
            cur = conn.execute(
                """INSERT INTO firmware_artifacts
                   (filename, version, source_type, source_ref, local_path,
                    size_bytes, md5, sha256, created_at, note)
                   VALUES(:filename,:version,:source_type,:source_ref,:local_path,
                          :size_bytes,:md5,:sha256,:created_at,:note)""",
                data,
            )
        return cur.lastrowid

    def list_artifacts(self) -> list:
        with self._conn() as conn:
            rows = conn.execute(
                "SELECT * FROM firmware_artifacts ORDER BY id DESC"
            ).fetchall()
        return [dict(r) for r in rows]

    def get_artifact(self, artifact_id: int) -> dict | None:
        with self._conn() as conn:
            row = conn.execute(
                "SELECT * FROM firmware_artifacts WHERE id=?", (artifact_id,)
            ).fetchone()
        return dict(row) if row else None

    # ------------------------------------------------------------------
    # upgrade_jobs
    # ------------------------------------------------------------------
    def insert_job(self, data: dict) -> int:
        data = dict(data)
        data.setdefault('validate_ok', 0)
        data.setdefault('reboot_ok', 0)
        with self._conn() as conn:
            cur = conn.execute(
                """INSERT INTO upgrade_jobs
                   (artifact_id, target_version, status, upload_ok, validate_ok,
                    trigger_ok, reboot_ok, online_ok, api_check, web_check,
                    duration_seconds, failure_reason, created_at)
                   VALUES(:artifact_id,:target_version,:status,:upload_ok,:validate_ok,
                          :trigger_ok,:reboot_ok,:online_ok,:api_check,:web_check,
                          :duration_seconds,:failure_reason,:created_at)""",
                data,
            )
        return cur.lastrowid

    def list_jobs(self) -> list:
        with self._conn() as conn:
            rows = conn.execute(
                "SELECT * FROM upgrade_jobs ORDER BY id DESC"
            ).fetchall()
        return [dict(r) for r in rows]

    # ------------------------------------------------------------------
    # experiment_runs
    # ------------------------------------------------------------------
    def insert_experiment(self, data: dict) -> int:
        with self._conn() as conn:
            cur = conn.execute(
                """INSERT INTO experiment_runs
                   (job_id, coverage, pass_rate, flaky_rate, duration_seconds,
                    failure_reason, created_at)
                   VALUES(:job_id,:coverage,:pass_rate,:flaky_rate,:duration_seconds,
                          :failure_reason,:created_at)""",
                data,
            )
        return cur.lastrowid

    def list_experiments(self) -> list:
        with self._conn() as conn:
            rows = conn.execute(
                "SELECT * FROM experiment_runs ORDER BY id DESC"
            ).fetchall()
        return [dict(r) for r in rows]

    def stats_summary(self) -> dict:
        with self._conn() as conn:
            total = conn.execute("SELECT COUNT(*) FROM upgrade_jobs").fetchone()[0]
            passed = conn.execute(
                "SELECT COUNT(*) FROM upgrade_jobs WHERE status='passed'"
            ).fetchone()[0]
            failed = total - passed
            avg_dur = conn.execute(
                "SELECT AVG(duration_seconds) FROM upgrade_jobs"
            ).fetchone()[0] or 0.0
            last_fail = conn.execute(
                "SELECT failure_reason FROM upgrade_jobs WHERE status='failed' ORDER BY id DESC LIMIT 1"
            ).fetchone()
            avg_cov = conn.execute(
                "SELECT AVG(coverage) FROM experiment_runs"
            ).fetchone()[0] or 0.0
            avg_flaky = conn.execute(
                "SELECT AVG(flaky_rate) FROM experiment_runs"
            ).fetchone()[0] or 0.0
        return {
            'total': total,
            'passed': passed,
            'failed': failed,
            'pass_rate': round(passed / total * 100, 1) if total else 0.0,
            'coverage': round(avg_cov * 100, 1),
            'flaky_rate': round(avg_flaky * 100, 1),
            'avg_duration': round(avg_dur, 2),
            'last_failure_reason': last_fail['failure_reason'] if last_fail else '—',
        }
