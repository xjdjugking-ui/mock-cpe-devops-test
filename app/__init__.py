from flask import Flask
from .config import Config
from .repository import StateRepository
from .service import GatewayService
from .routes import bp, api


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    repo = StateRepository(app.config['DATABASE_PATH'])
    repo.init_db()
    app.gateway_service = GatewayService(repo)

    app.register_blueprint(bp)
    app.register_blueprint(api)

    return app
