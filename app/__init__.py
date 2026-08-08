from flask import Flask
from flask_cors import CORS

from app.errors import register_error_handlers
from app.extensions import db
from app.routes.user_routes import user_bp
from config import config_by_name


def create_app(config_name="development"):
    app = Flask(__name__)
    app.config.from_object(config_by_name[config_name])

    db.init_app(app)
    CORS(app, origins=app.config["CORS_ORIGINS"])

    app.register_blueprint(user_bp)

    register_error_handlers(app)

    return app
