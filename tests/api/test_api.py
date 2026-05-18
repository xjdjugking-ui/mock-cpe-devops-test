"""API tests using Flask test client — no browser, no real CPE."""
import pytest
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))


@pytest.fixture
def client(tmp_path):
    os.environ['DATABASE_PATH'] = str(tmp_path / "test_api.db")
    from app import create_app
    app = create_app()
    app.config['TESTING'] = True
    app.config['DATABASE_PATH'] = str(tmp_path / "test_api.db")
    # re-init with test db
    from app.repository import StateRepository
    from app.service import GatewayService
    repo = StateRepository(app.config['DATABASE_PATH'])
    repo.init_db()
    app.gateway_service = GatewayService(repo)
    with app.test_client() as c:
        yield c


def _login(client):
    client.post('/login', data={'username': 'admin', 'password': 'admin123'},
                follow_redirects=True)


# ------------------------------------------------------------------
# Health / Readiness
# ------------------------------------------------------------------
def test_health_api(client):
    r = client.get('/api/v1/health')
    assert r.status_code == 200
    assert r.get_json()['status'] == 'ok'


def test_readiness_api(client):
    r = client.get('/api/v1/readiness')
    assert r.status_code == 200
    assert r.get_json()['ready'] is True


def test_build_info_api(client):
    r = client.get('/api/v1/build-info')
    assert r.status_code == 200
    data = r.get_json()
    assert data['version']
    assert 'build_number' in data
    assert 'build_url' in data


def test_ci_firmware_target_is_applied_on_startup(tmp_path, monkeypatch):
    monkeypatch.setenv('DATABASE_PATH', str(tmp_path / "test_ci_firmware.db"))
    monkeypatch.setenv('APP_BUILD_VERSION', 'Build #999')
    monkeypatch.setenv('APP_BUILD_NUMBER', '999')
    monkeypatch.setenv('APP_BUILD_URL', 'http://jenkins/job/999/')
    monkeypatch.setenv('APP_FIRMWARE_BASELINE', 'v2.0.1')
    monkeypatch.setenv('APP_FIRMWARE_TARGET', 'v6.00')

    from app import create_app
    app = create_app()
    app.config['TESTING'] = True

    with app.test_client() as c:
        r = c.get('/api/v1/dashboard')
        assert r.status_code == 200
        data = r.get_json()
        assert data['firmware_version'] == 'v6.0.0'
        assert data['last_upgrade_version'] == '6.0.0'
        assert any(
            'from v2.0.1 to v6.0.0' in item['detail']
            for item in data['activities']
        )


def test_ci_firmware_baseline_only_is_applied_on_startup(tmp_path, monkeypatch):
    monkeypatch.setenv('DATABASE_PATH', str(tmp_path / "test_ci_baseline.db"))
    monkeypatch.setenv('APP_BUILD_VERSION', 'Build #1000')
    monkeypatch.setenv('APP_BUILD_NUMBER', '1000')
    monkeypatch.setenv('APP_BUILD_URL', 'http://jenkins/job/1000/')
    monkeypatch.setenv('APP_FIRMWARE_BASELINE', '2.0.1')
    monkeypatch.setenv('APP_FIRMWARE_TARGET', '')

    from app import create_app
    app = create_app()
    app.config['TESTING'] = True

    with app.test_client() as c:
        r = c.get('/api/v1/dashboard')
        assert r.status_code == 200
        data = r.get_json()
        assert data['firmware_version'] == 'v2.0.1'
        assert data['last_upgrade_status'] == 'baseline'
        assert any(
            'baseline set to v2.0.1' in item['detail']
            for item in data['activities']
        )


# ------------------------------------------------------------------
# Dashboard
# ------------------------------------------------------------------
def test_dashboard_api(client):
    r = client.get('/api/v1/dashboard')
    assert r.status_code == 200
    data = r.get_json()
    assert 'firmware_version' in data
    assert 'wan_status' in data
    assert 'client_count' in data


# ------------------------------------------------------------------
# Network
# ------------------------------------------------------------------
def test_get_network_api(client):
    r = client.get('/api/v1/network')
    assert r.status_code == 200
    data = r.get_json()
    assert 'ssid' in data
    assert 'mode' in data


def test_update_network_api(client):
    r = client.post('/api/v1/network',
                    json={'ssid': 'NewSSID', 'mode': 'static', 'channel': '11'})
    assert r.status_code == 200
    assert r.get_json()['ok'] is True
    # verify persisted
    r2 = client.get('/api/v1/network')
    assert r2.get_json()['ssid'] == 'NewSSID'


# ------------------------------------------------------------------
# Firmware validation
# ------------------------------------------------------------------
def test_validate_valid_firmware_api(client):
    r = client.post('/api/v1/upgrade',
                    json={'filename': 'cpe_gateway_v3.0.0.bin'})
    assert r.status_code == 200
    data = r.get_json()
    assert data['status'] == 'validated'
    assert data['version'] == '3.0.0'


def test_validate_invalid_firmware_api(client):
    r = client.post('/api/v1/upgrade',
                    json={'filename': 'bad_firmware.zip'})
    assert r.status_code == 200
    data = r.get_json()
    assert data['status'] == 'rejected'
    assert data['version'] is None


# ------------------------------------------------------------------
# Artifacts
# ------------------------------------------------------------------
def test_get_artifacts_api(client):
    r = client.get('/api/v1/artifacts')
    assert r.status_code == 200
    assert isinstance(r.get_json(), list)


def test_register_artifact_api(client):
    r = client.post('/api/v1/artifacts', json={
        'filename': 'cpe_gateway_v9.0.0.bin',
        'source_type': 'ci',
        'source_ref': 'build-99',
        'note': 'api test',
    })
    assert r.status_code == 201
    data = r.get_json()
    assert data['ok'] is True
    assert 'id' in data


def test_register_invalid_artifact_api(client):
    r = client.post('/api/v1/artifacts', json={'filename': 'invalid.exe'})
    assert r.status_code == 400
    assert r.get_json()['ok'] is False


# ------------------------------------------------------------------
# Upgrade jobs
# ------------------------------------------------------------------
def test_run_upgrade_job_api(client):
    # register artifact first
    r1 = client.post('/api/v1/artifacts', json={
        'filename': 'cpe_gateway_v8.0.0.bin',
        'source_type': 'manual',
    })
    artifact_id = r1.get_json()['id']
    r2 = client.post('/api/v1/upgrade-jobs', json={'artifact_id': artifact_id})
    assert r2.status_code == 200
    data = r2.get_json()
    assert data['ok'] is True
    assert data['status'] == 'passed'


def test_run_upgrade_job_missing_artifact_id(client):
    r = client.post('/api/v1/upgrade-jobs', json={})
    assert r.status_code == 400
    assert r.get_json()['ok'] is False


def test_get_upgrade_jobs_api(client):
    r = client.get('/api/v1/upgrade-jobs')
    assert r.status_code == 200
    assert isinstance(r.get_json(), list)


# ------------------------------------------------------------------
# Experiments
# ------------------------------------------------------------------
def test_experiments_api(client):
    r = client.get('/api/v1/experiments')
    assert r.status_code == 200
    data = r.get_json()
    assert 'summary' in data
    assert 'records' in data
    assert 'total' in data['summary']


# ------------------------------------------------------------------
# Diagnostics
# ------------------------------------------------------------------
def test_get_diagnostics_api(client):
    r = client.get('/api/v1/diagnostics')
    assert r.status_code == 200
    data = r.get_json()
    assert 'ping' in data
    assert 'dns' in data
    assert 'cloud' in data


def test_refresh_diagnostics_api(client):
    r = client.post('/api/v1/diagnostics')
    assert r.status_code == 200
    data = r.get_json()
    assert data['ping'] == 'ok'
    assert 'packet_loss' in data
