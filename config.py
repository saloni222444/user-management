import os

from dotenv import load_dotenv
from sqlalchemy.pool import NullPool

load_dotenv()

# Bound how long a single query (including a lock wait) can take, so a
# stuck connection fails fast with a clear error instead of hanging the
# app - or a test run - indefinitely.
_CONNECT_TIMEOUTS = {"connect_timeout": 10, "read_timeout": 30, "write_timeout": 30}


class Config:
    """Base configuration shared by all environments."""

    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key")
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,
        "connect_args": _CONNECT_TIMEOUTS,
    }
    # Origins allowed to call the API from a browser (the Vite admin UI dev
    # server). Comma-separated so it can be overridden per environment.
    CORS_ORIGINS = os.environ.get(
        "CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173"
    ).split(",")


class DevelopmentConfig(Config):
    DEBUG = True


class TestingConfig(Config):
    TESTING = True
    DEBUG = True
    # Falls back to DATABASE_URL only if TEST_DATABASE_URL is not set, but the
    # test suite refuses to run unless the resolved URL clearly points at a
    # test database (see tests/conftest.py).
    SQLALCHEMY_DATABASE_URI = os.environ.get("TEST_DATABASE_URL", os.environ.get("DATABASE_URL"))
    # NullPool: each test gets a fresh connection instead of sharing a
    # pooled one across the session, which keeps test isolation simple.
    SQLALCHEMY_ENGINE_OPTIONS = {
        "poolclass": NullPool,
        "connect_args": _CONNECT_TIMEOUTS,
    }


class ProductionConfig(Config):
    DEBUG = False


config_by_name = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
}
