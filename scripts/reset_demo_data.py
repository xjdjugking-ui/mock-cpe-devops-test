"""
Reset demo data — clears all jobs, experiments, and artifacts, then seeds
a clean set of passing upgrade jobs for thesis screenshots.

Usage:
    python scripts/reset_demo_data.py
"""
import sys
import os
import sqlite3
import hashlib
import random
from datetime import datetime, timedelta

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'mock_cpe.db')


def conn():
    c = sqlite3.connect(DB_PATH)
    c.row_factory = sqlite3.Row
    return c


def reset():
    with conn() as db:
        db.execute("DELETE FROM upgrade_jobs")
        db.execute("DELETE FROM experiment_runs")
        db.execute("DELETE FROM firmware_artifacts")
        db.execute("DELETE FROM activities WHERE event IN ('制品登记','升级任务','固件校验')")
        db.execute("UPDATE singleton_state SET payload=json_set(payload,'$.last_status','none','$.last_version',null,'$.last_time',null) WHERE section='upgrade'")
        db.execute("UPDATE singleton_state SET payload=json_set(payload,'$.firmware_version','v2.1.0') WHERE section='system'")

    artifacts = [
        ('cpe_gateway_v3.0.0.bin', '3.0.0'),
        ('cpe_gateway_v4.0.0.bin', '4.0.0'),
        ('cpe_gateway_v5.0.0.bin', '5.0.0'),
        ('cpe_gateway_v6.0.0.bin', '6.0.0'),
        ('cpe_gateway_v7.0.0.bin', '7.0.0'),
    ]

    base_time = datetime.now() - timedelta(hours=len(artifacts))
    artifact_ids = []

    with conn() as db:
        for i, (filename, version) in enumerate(artifacts):
            ts = (base_time + timedelta(minutes=i * 10)).strftime('%Y-%m-%d %H:%M:%S')
            seed = filename + ts
            md5 = hashlib.md5(seed.encode()).hexdigest()
            sha256 = hashlib.sha256(seed.encode()).hexdigest()
            size = random.randint(5 * 1024 * 1024, 20 * 1024 * 1024)
            cur = db.execute(
                """INSERT INTO firmware_artifacts
                   (filename, version, source_type, source_ref, local_path,
                    size_bytes, md5, sha256, created_at, note)
                   VALUES (?,?,?,?,?,?,?,?,?,?)""",
                (filename, version, 'ci', f'build-{1000+i}',
                 f'artifacts/{filename}', size, md5, sha256, ts,
                 '演示制品'),
            )
            artifact_ids.append((cur.lastrowid, version, filename, ts))

    with conn() as db:
        for art_id, version, filename, art_ts in artifact_ids:
            job_ts = (datetime.strptime(art_ts, '%Y-%m-%d %H:%M:%S') + timedelta(minutes=2)).strftime('%Y-%m-%d %H:%M:%S')
            duration = round(random.uniform(1.2, 3.5), 2)
            cur = db.execute(
                """INSERT INTO upgrade_jobs
                   (artifact_id, target_version, status, upload_ok, trigger_ok,
                    online_ok, api_check, web_check, duration_seconds,
                    failure_reason, created_at)
                   VALUES (?,?,?,?,?,?,?,?,?,?,?)""",
                (art_id, version, 'passed', 1, 1, 1, 1, 1, duration, None, job_ts),
            )
            job_id = cur.lastrowid
            coverage = round(random.uniform(0.88, 0.97), 4)
            flaky = round(random.uniform(0.00, 0.03), 4)
            db.execute(
                """INSERT INTO experiment_runs
                   (job_id, coverage, pass_rate, flaky_rate, duration_seconds,
                    failure_reason, created_at)
                   VALUES (?,?,?,?,?,?,?)""",
                (job_id, coverage, 1.0, flaky, duration, None, job_ts),
            )

        # update system state to latest version
        latest_version = artifact_ids[-1][1]
        latest_ts = (datetime.strptime(artifact_ids[-1][3], '%Y-%m-%d %H:%M:%S') + timedelta(minutes=2)).strftime('%Y-%m-%d %H:%M:%S')
        db.execute(
            "UPDATE singleton_state SET payload=json_set(payload,'$.firmware_version',?) WHERE section='system'",
            (f'v{latest_version}',),
        )
        db.execute(
            """UPDATE singleton_state SET payload=json_set(
                payload,'$.last_status','passed',
                '$.last_version',?,
                '$.last_time',?
            ) WHERE section='upgrade'""",
            (latest_version, latest_ts),
        )

        db.execute("INSERT INTO activities(time,event,detail) VALUES(?,?,?)",
                   (latest_ts, '升级任务', f'演示数据重置完成，最新固件 v{latest_version} 升级成功'))

    print(f"Demo data reset complete. {len(artifact_ids)} artifacts and jobs seeded, all PASSED.")


if __name__ == '__main__':
    reset()
