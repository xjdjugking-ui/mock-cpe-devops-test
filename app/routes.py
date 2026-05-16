from functools import wraps
from flask import (Blueprint, render_template, request, redirect,
                   url_for, session, flash, jsonify, current_app)

bp = Blueprint('main', __name__)


# ------------------------------------------------------------------
# Auth helpers
# ------------------------------------------------------------------
def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get('user'):
            return redirect(url_for('main.login'))
        return f(*args, **kwargs)
    return decorated


def _svc():
    return current_app.gateway_service


# ------------------------------------------------------------------
# Auth routes
# ------------------------------------------------------------------
@bp.route('/')
def index():
    return redirect(url_for('main.dashboard'))


@bp.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form.get('username', '')
        password = request.form.get('password', '')
        cfg = current_app.config
        if username == cfg['ADMIN_USERNAME'] and password == cfg['ADMIN_PASSWORD']:
            session['user'] = username
            return redirect(url_for('main.dashboard'))
        error = '用户名或密码错误'
    return render_template('login.html', error=error)


@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('main.login'))


# ------------------------------------------------------------------
# Dashboard
# ------------------------------------------------------------------
@bp.route('/dashboard')
@login_required
def dashboard():
    ctx = _svc().dashboard_context()
    return render_template('dashboard.html', active='dashboard', **ctx)


# ------------------------------------------------------------------
# Network
# ------------------------------------------------------------------
@bp.route('/network', methods=['GET', 'POST'])
@login_required
def network():
    message = None
    if request.method == 'POST':
        _svc().update_network(request.form.to_dict())
        message = '网络配置已保存'
    net = _svc().get_network()
    return render_template('network.html', active='network', config=net, message=message)


# ------------------------------------------------------------------
# Upgrade
# ------------------------------------------------------------------
@bp.route('/upgrade', methods=['GET', 'POST'])
@login_required
def upgrade():
    result = None
    if request.method == 'POST':
        filename = request.form.get('firmware-filename', '')
        result = _svc().validate_firmware(filename)
    return render_template('upgrade.html', active='upgrade', result=result)


# ------------------------------------------------------------------
# Diagnostics
# ------------------------------------------------------------------
@bp.route('/diagnostics', methods=['GET', 'POST'])
@login_required
def diagnostics():
    message = None
    if request.method == 'POST':
        diag = _svc().run_diagnostics()
        message = '诊断已刷新'
    else:
        diag = _svc().get_diagnostics()
    return render_template('diagnostics.html', active='diagnostics', diag=diag, message=message)


# ------------------------------------------------------------------
# Artifacts
# ------------------------------------------------------------------
@bp.route('/artifacts', methods=['GET', 'POST'])
@login_required
def artifacts():
    message = None
    msg_type = 'success'
    if request.method == 'POST':
        res = _svc().register_artifact(request.form.to_dict())
        message = res['message']
        msg_type = 'success' if res['ok'] else 'error'
    artifact_list = _svc().list_artifacts()
    return render_template('artifacts.html', active='artifacts',
                           artifacts=artifact_list, message=message, msg_type=msg_type)


# ------------------------------------------------------------------
# Jobs
# ------------------------------------------------------------------
@bp.route('/jobs', methods=['GET', 'POST'])
@login_required
def jobs():
    message = None
    msg_type = 'success'
    job_result = None
    if request.method == 'POST':
        artifact_id = request.form.get('artifact-select', '')
        if artifact_id:
            job_result = _svc().run_upgrade_job(int(artifact_id))
            message = job_result['message']
            msg_type = 'success' if job_result['ok'] else 'error'
        else:
            message = '请先选择一个固件制品'
            msg_type = 'error'
    artifact_list = _svc().list_artifacts()
    jobs_list = _svc().list_jobs()
    return render_template('jobs.html', active='jobs',
                           artifact_list=artifact_list, jobs_list=jobs_list,
                           message=message, msg_type=msg_type, job_result=job_result)


# ------------------------------------------------------------------
# Stats
# ------------------------------------------------------------------
@bp.route('/stats')
@login_required
def stats():
    summary = _svc().stats_summary()
    experiments = _svc().list_experiments()
    return render_template('stats.html', active='stats', summary=summary, experiments=experiments)


# ==================================================================
# API v1
# ==================================================================
api = Blueprint('api', __name__, url_prefix='/api/v1')


@api.route('/health')
def health():
    return jsonify({'status': 'ok'})


@api.route('/readiness')
def readiness():
    return jsonify({'ready': True})


@api.route('/dashboard')
def api_dashboard():
    return jsonify(_svc().dashboard_context())


@api.route('/network', methods=['GET', 'POST'])
def api_network():
    if request.method == 'POST':
        _svc().update_network(request.get_json(force=True) or {})
        return jsonify({'ok': True, 'message': '网络配置已保存'})
    return jsonify(_svc().get_network())


@api.route('/upgrade', methods=['POST'])
def api_upgrade():
    body = request.get_json(force=True) or {}
    return jsonify(_svc().validate_firmware(body.get('filename', '')))


@api.route('/artifacts', methods=['GET', 'POST'])
def api_artifacts():
    if request.method == 'POST':
        res = _svc().register_artifact(request.get_json(force=True) or {})
        code = 201 if res['ok'] else 400
        return jsonify(res), code
    return jsonify(_svc().list_artifacts())


@api.route('/upgrade-jobs', methods=['GET', 'POST'])
def api_upgrade_jobs():
    if request.method == 'POST':
        body = request.get_json(force=True) or {}
        artifact_id = body.get('artifact_id')
        if not artifact_id:
            return jsonify({'ok': False, 'message': 'artifact_id 必填'}), 400
        return jsonify(_svc().run_upgrade_job(int(artifact_id)))
    return jsonify(_svc().list_jobs())


@api.route('/experiments')
def api_experiments():
    return jsonify({
        'summary': _svc().stats_summary(),
        'records': _svc().list_experiments(),
    })


@api.route('/diagnostics', methods=['GET', 'POST'])
def api_diagnostics():
    if request.method == 'POST':
        return jsonify(_svc().run_diagnostics())
    return jsonify(_svc().get_diagnostics())
