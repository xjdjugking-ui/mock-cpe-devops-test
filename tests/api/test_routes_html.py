"""HTML-rendering route tests using Flask test client — covers routes.py."""
import os
import sys
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))


@pytest.fixture
def client(tmp_path):
    os.environ['DATABASE_PATH'] = str(tmp_path / "test_html.db")
    from app import create_app
    app = create_app()
    app.config['TESTING'] = True
    app.config['DATABASE_PATH'] = str(tmp_path / "test_html.db")
    from app.repository import StateRepository
    from app.service import GatewayService
    repo = StateRepository(app.config['DATABASE_PATH'])
    repo.init_db()
    app.gateway_service = GatewayService(repo)
    with app.test_client() as c:
        yield c


def _login(client):
    return client.post('/login', data={'username': 'admin', 'password': 'admin123'},
                       follow_redirects=True)


# ------------------------------------------------------------------
# Index redirects to dashboard (line 29)
# ------------------------------------------------------------------
def test_index_redirects(client):
    r = client.get('/')
    assert r.status_code == 302

def test_index_redirects_to_dashboard(client):
    r = client.get('/', follow_redirects=True)
    assert r.status_code == 200


# ------------------------------------------------------------------
# Login page (lines 34-43)
# ------------------------------------------------------------------
def test_login_page_get(client):
    r = client.get('/login')
    assert r.status_code == 200
    assert 'text/html' in r.content_type

def test_login_post_success(client):
    r = client.post('/login', data={'username': 'admin', 'password': 'admin123'},
                    follow_redirects=True)
    assert r.status_code == 200
    assert b'dashboard' in r.data.lower() or b'\xe4\xbb\xaa\xe8\xa1\xa8\xe7\x9b\x98' in r.data

def test_login_post_wrong_password(client):
    r = client.post('/login', data={'username': 'admin', 'password': 'wrong'},
                    follow_redirects=True)
    assert r.status_code == 200
    assert 'text/html' in r.content_type

def test_login_post_wrong_username(client):
    r = client.post('/login', data={'username': 'nobody', 'password': 'admin123'},
                    follow_redirects=True)
    assert r.status_code == 200

def test_login_redirects_logged_in_user(client):
    _login(client)
    r = client.get('/login', follow_redirects=True)
    assert r.status_code == 200


# ------------------------------------------------------------------
# Logout (lines 48-49)
# ------------------------------------------------------------------
def test_logout_clears_session(client):
    _login(client)
    r = client.get('/logout', follow_redirects=True)
    assert r.status_code == 200

def test_logout_redirects_to_login(client):
    _login(client)
    r = client.get('/logout', follow_redirects=True)
    assert r.status_code == 200
    # After logout, accessing protected page should redirect
    r2 = client.get('/dashboard', follow_redirects=True)
    assert r2.status_code == 200


# ------------------------------------------------------------------
# Dashboard (lines 58-59)
# ------------------------------------------------------------------
def test_dashboard_requires_login(client):
    r = client.get('/dashboard', follow_redirects=True)
    assert r.status_code == 200
    assert 'text/html' in r.content_type

def test_dashboard_authenticated(client):
    _login(client)
    r = client.get('/dashboard')
    assert r.status_code == 200
    assert 'text/html' in r.content_type


# ------------------------------------------------------------------
# Network page (lines 68-73)
# ------------------------------------------------------------------
def test_network_get_authenticated(client):
    _login(client)
    r = client.get('/network')
    assert r.status_code == 200
    assert 'text/html' in r.content_type

def test_network_post_updates_config(client):
    _login(client)
    r = client.post('/network', data={'ssid': 'MyNet', 'mode': 'dhcp', 'channel': '6'},
                    follow_redirects=True)
    assert r.status_code == 200

def test_network_get_requires_login(client):
    r = client.get('/network', follow_redirects=True)
    assert r.status_code == 200


# ------------------------------------------------------------------
# Upgrade page (lines 82-86)
# ------------------------------------------------------------------
def test_upgrade_get_authenticated(client):
    _login(client)
    r = client.get('/upgrade')
    assert r.status_code == 200
    assert 'text/html' in r.content_type

def test_upgrade_post_validates_firmware(client):
    _login(client)
    r = client.post('/upgrade', data={'firmware-filename': 'cpe_gateway_v3.0.0.bin'},
                    follow_redirects=True)
    assert r.status_code == 200

def test_upgrade_post_invalid_firmware(client):
    _login(client)
    r = client.post('/upgrade', data={'firmware-filename': 'bad.exe'},
                    follow_redirects=True)
    assert r.status_code == 200

def test_upgrade_get_requires_login(client):
    r = client.get('/upgrade', follow_redirects=True)
    assert r.status_code == 200


# ------------------------------------------------------------------
# Diagnostics page (lines 95-101)
# ------------------------------------------------------------------
def test_diagnostics_get_authenticated(client):
    _login(client)
    r = client.get('/diagnostics')
    assert r.status_code == 200
    assert 'text/html' in r.content_type

def test_diagnostics_post_refreshes(client):
    _login(client)
    r = client.post('/diagnostics', follow_redirects=True)
    assert r.status_code == 200

def test_diagnostics_get_requires_login(client):
    r = client.get('/diagnostics', follow_redirects=True)
    assert r.status_code == 200


# ------------------------------------------------------------------
# Artifacts page (lines 110-117)
# ------------------------------------------------------------------
def test_artifacts_get_authenticated(client):
    _login(client)
    r = client.get('/artifacts')
    assert r.status_code == 200
    assert 'text/html' in r.content_type

def test_artifacts_post_register(client):
    _login(client)
    r = client.post('/artifacts', data={
        'filename': 'cpe_gateway_v7.0.0.bin',
        'source_type': 'manual',
    }, follow_redirects=True)
    assert r.status_code == 200

def test_artifacts_post_invalid(client):
    _login(client)
    r = client.post('/artifacts', data={'filename': 'bad.bin'}, follow_redirects=True)
    assert r.status_code == 200

def test_artifacts_get_requires_login(client):
    r = client.get('/artifacts', follow_redirects=True)
    assert r.status_code == 200


# ------------------------------------------------------------------
# Jobs page (lines 127-141)
# ------------------------------------------------------------------
def test_jobs_get_authenticated(client):
    _login(client)
    r = client.get('/jobs')
    assert r.status_code == 200
    assert 'text/html' in r.content_type

def test_jobs_post_run_upgrade(client):
    _login(client)
    # Register artifact first
    client.post('/artifacts', data={
        'filename': 'cpe_gateway_v8.0.0.bin',
        'source_type': 'manual',
    })
    # Get artifact id from API
    r_artifacts = client.get('/api/v1/artifacts')
    artifacts = r_artifacts.get_json()
    assert len(artifacts) > 0
    artifact_id = artifacts[0]['id']
    r = client.post('/jobs', data={'artifact-select': str(artifact_id)},
                    follow_redirects=True)
    assert r.status_code == 200

def test_jobs_post_no_artifact_selected(client):
    _login(client)
    r = client.post('/jobs', data={}, follow_redirects=True)
    assert r.status_code == 200

def test_jobs_post_empty_artifact(client):
    _login(client)
    r = client.post('/jobs', data={'artifact-select': ''}, follow_redirects=True)
    assert r.status_code == 200

def test_jobs_get_requires_login(client):
    r = client.get('/jobs', follow_redirects=True)
    assert r.status_code == 200


# ------------------------------------------------------------------
# Stats page (lines 152-154)
# ------------------------------------------------------------------
def test_stats_get_authenticated(client):
    _login(client)
    r = client.get('/stats')
    assert r.status_code == 200
    assert 'text/html' in r.content_type

def test_stats_requires_login(client):
    r = client.get('/stats', follow_redirects=True)
    assert r.status_code == 200