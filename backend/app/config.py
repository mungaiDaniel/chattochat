"""Application configuration, driven entirely by environment variables.

Select a profile with ``APP_ENV`` (``development`` | ``testing`` | ``production``).
See ``.env.example`` for the full list of variables.
"""
import os
import secrets
from datetime import timedelta
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent


def _database_url(default: str | None = None) -> str | None:
    url = os.environ.get("DATABASE_URL", default)
    # Heroku-style URLs use the legacy "postgres://" scheme, which SQLAlchemy rejects.
    if url and url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql+psycopg2://", 1)
    elif url and url.startswith("postgresql://"):
        url = url.replace("postgresql://", "postgresql+psycopg2://", 1)
    return url


def _origins() -> list[str]:
    raw = os.environ.get("CORS_ORIGINS", "http://localhost:3000")
    return [o.strip() for o in raw.split(",") if o.strip()]


class Config:
    DEBUG = False
    TESTING = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    JWT_ACCESS_TOKEN_EXPIRES = timedelta(
        minutes=int(os.environ.get("JWT_ACCESS_MINUTES", "60"))
    )
    UPLOAD_FOLDER = os.environ.get("UPLOAD_FOLDER", str(BASE_DIR / "uploads"))
    MAX_CONTENT_LENGTH = 8 * 1024 * 1024  # 8 MB per request
    CORS_ORIGINS = _origins()
    RATELIMIT_ENABLED = True
    RATELIMIT_STORAGE_URI = os.environ.get("RATELIMIT_STORAGE_URI", "memory://")


class DevelopmentConfig(Config):
    DEBUG = True
    # A random per-process key is fine for local work (tokens just expire on restart).
    SECRET_KEY = os.environ.get("SECRET_KEY") or secrets.token_hex(32)
    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY") or secrets.token_hex(32)
    # Zero-setup default: a local SQLite file. Set DATABASE_URL to use PostgreSQL.
    SQLALCHEMY_DATABASE_URI = _database_url(f"sqlite:///{BASE_DIR / 'chat2chat.db'}")


class TestingConfig(Config):
    TESTING = True
    SECRET_KEY = "test-secret-key"
    JWT_SECRET_KEY = "test-jwt-secret-key-with-sufficient-length"
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    RATELIMIT_ENABLED = False
    PASSWORD_HASH_METHOD = "pbkdf2:sha256:1000"  # fast hashing keeps the test suite quick
    CORS_ORIGINS = ["http://localhost:3000"]


class ProductionConfig(Config):
    SECRET_KEY = os.environ.get("SECRET_KEY")
    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY")
    SQLALCHEMY_DATABASE_URI = _database_url()

    @classmethod
    def validate(cls) -> None:
        """Refuse to boot without real secrets and a database."""
        missing = [
            name
            for name in ("SECRET_KEY", "JWT_SECRET_KEY", "DATABASE_URL")
            if not os.environ.get(name)
        ]
        if missing:
            raise RuntimeError(
                "Missing required environment variables for production: "
                + ", ".join(missing)
            )


CONFIGS = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
}


def get_config(name: str | None = None) -> type[Config]:
    name = name or os.environ.get("APP_ENV", "development")
    try:
        return CONFIGS[name]
    except KeyError:
        raise RuntimeError(f"Unknown APP_ENV '{name}'. Use one of: {', '.join(CONFIGS)}")
