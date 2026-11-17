"""Chat2Chat API application factory."""
import logging
from pathlib import Path

from flask import Flask, send_from_directory
from sqlalchemy import text

from .api import API_PREFIX, BLUEPRINTS
from .config import ProductionConfig, get_config
from .errors import register_error_handlers
from .extensions import cors, db, jwt, limiter, migrate


def create_app(config_name: str | None = None) -> Flask:
    app = Flask(__name__)
    config = get_config(config_name)
    if config is ProductionConfig:
        ProductionConfig.validate()
    app.config.from_object(config)

    logging.basicConfig(level=logging.DEBUG if app.debug else logging.INFO)

    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    limiter.init_app(app)
    cors.init_app(app, resources={r"/*": {"origins": app.config["CORS_ORIGINS"]}})

    register_error_handlers(app)
    for bp in BLUEPRINTS:
        app.register_blueprint(bp, url_prefix=API_PREFIX)

    @app.get(f"{API_PREFIX}/health")
    def health():
        """Liveness + database connectivity probe."""
        db.session.execute(text("SELECT 1"))
        return {"status": 200, "data": {"service": "chat2chat-api", "database": "ok"}}

    @app.get("/uploads/<path:filename>")
    def uploaded_file(filename: str):
        # send_from_directory rejects paths that escape the upload folder.
        folder = Path(app.config["UPLOAD_FOLDER"])
        return send_from_directory(folder, filename)

    return app
