import os
from datetime import datetime

from flask import Flask
from .config import Config
from .repository import StateRepository
from .service import GatewayService
from .routes import bp, api


def _normalize_firmware_version(value):
    value = (value or '').strip()
    if not value:
        return ''
    raw = value[1:] if value.startswith('v') else value
    try:
        parts = [int(part) for part in raw.split('.') if part != '']
    except ValueError:
        return value if value.startswith('v') else f'v{value}'
    if not 1 <= len(parts) <= 3:
        return value if value.startswith('v') else f'v{value}'
    while len(parts) < 3:
        parts.append(0)
    return f'v{parts[0]}.{parts[1]}.{parts[2]}'


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    for key, default in {
        'APP_BUILD_VERSION': 'local-dev',
        'APP_BUILD_NUMBER': '',
        'APP_BUILD_URL': '',
        'APP_FIRMWARE_BASELINE': '',
        'APP_FIRMWARE_TARGET': '',
    }.items():
        app.config[key] = os.environ.get(key, app.config.get(key, default))

    repo = StateRepository(app.config['DATABASE_PATH'])
    repo.init_db()
    build_number = app.config.get('APP_BUILD_NUMBER', '')
    if build_number:
        deployment = repo.get_state('deployment')
        baseline_firmware = _normalize_firmware_version(
            app.config.get('APP_FIRMWARE_BASELINE', '')
        )
        target_firmware = _normalize_firmware_version(app.config.get('APP_FIRMWARE_TARGET', ''))
        if (deployment.get('build_number') != build_number or
                deployment.get('baseline_firmware') != baseline_firmware or
                deployment.get('target_firmware') != target_firmware):
            build_version = app.config.get('APP_BUILD_VERSION', 'local-dev')
            build_url = app.config.get('APP_BUILD_URL', '')
            if target_firmware:
                system_state = repo.get_state('system')
                current_firmware = system_state.get('firmware_version', 'v2.1.0')
                baseline = baseline_firmware or current_firmware
                system_state['firmware_version'] = target_firmware
                repo.set_state('system', system_state)
                upgrade_state = repo.get_state('upgrade')
                upgrade_state.update({
                    'last_status': 'passed',
                    'last_version': target_firmware.lstrip('v'),
                    'last_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                })
                repo.set_state('upgrade', upgrade_state)
                repo.add_activity(
                    'CI Firmware Upgrade',
                    f"Gateway firmware upgraded from {baseline} to {target_firmware} by {build_version}",
                )
            elif baseline_firmware:
                system_state = repo.get_state('system')
                system_state['firmware_version'] = baseline_firmware
                repo.set_state('system', system_state)
                upgrade_state = repo.get_state('upgrade')
                upgrade_state.update({
                    'last_status': 'baseline',
                    'last_version': baseline_firmware.lstrip('v'),
                    'last_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                })
                repo.set_state('upgrade', upgrade_state)
                repo.add_activity(
                    'CI Baseline',
                    f"Gateway firmware baseline set to {baseline_firmware} before Jenkins validation by {build_version}",
                )
            repo.add_activity(
                'CI Deploy',
                f"{build_version} passed Jenkins tests and redeployed gateway web",
            )
            repo.set_state('deployment', {
                'build_number': build_number,
                'version': build_version,
                'build_url': build_url,
                'baseline_firmware': baseline_firmware,
                'target_firmware': target_firmware,
            })
    app.gateway_service = GatewayService(repo)

    @app.context_processor
    def inject_build_info():
        return {
            'app_build_version': app.config.get('APP_BUILD_VERSION', 'local-dev'),
            'app_build_number': app.config.get('APP_BUILD_NUMBER', ''),
            'app_build_url': app.config.get('APP_BUILD_URL', ''),
        }

    app.register_blueprint(bp)
    app.register_blueprint(api)

    return app
