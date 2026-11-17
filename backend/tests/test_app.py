import pytest

from app import create_app
from app.config import ProductionConfig


def test_health_reports_database_ok(client):
    resp = client.get("/api/v1/health")
    assert resp.status_code == 200
    assert resp.get_json()["data"]["database"] == "ok"


def test_unknown_route_returns_json_404(client):
    resp = client.get("/api/v1/nope")
    assert resp.status_code == 404
    assert resp.get_json()["status"] == 404


def test_wrong_method_returns_json_405(client):
    resp = client.delete("/api/v1/user")
    assert resp.status_code == 405
    assert resp.get_json()["status"] == 405


def test_unexpected_exception_returns_generic_500(app):
    @app.get("/boom")
    def boom():
        raise RuntimeError("secret internal detail")

    app.config["PROPAGATE_EXCEPTIONS"] = False
    resp = app.test_client().get("/boom")
    assert resp.status_code == 500
    assert "secret internal detail" not in resp.get_data(as_text=True)


def test_cors_allows_configured_origin_only(client):
    ok = client.get("/api/v1/health", headers={"Origin": "http://localhost:3000"})
    bad = client.get("/api/v1/health", headers={"Origin": "http://evil.example"})
    assert ok.headers.get("Access-Control-Allow-Origin") == "http://localhost:3000"
    assert "Access-Control-Allow-Origin" not in bad.headers


def test_production_refuses_to_start_without_secrets(monkeypatch):
    for var in ("SECRET_KEY", "JWT_SECRET_KEY", "DATABASE_URL"):
        monkeypatch.delenv(var, raising=False)
    with pytest.raises(RuntimeError, match="SECRET_KEY"):
        create_app("production")


def test_production_validation_passes_when_configured(monkeypatch):
    monkeypatch.setenv("SECRET_KEY", "a")
    monkeypatch.setenv("JWT_SECRET_KEY", "b")
    monkeypatch.setenv("DATABASE_URL", "postgresql://u:p@localhost/db")
    ProductionConfig.validate()  # does not raise


def test_unknown_env_name_rejected():
    with pytest.raises(RuntimeError, match="Unknown APP_ENV"):
        create_app("staging")


def test_postgres_url_schemes_are_normalised(monkeypatch):
    from app.config import _database_url

    monkeypatch.setenv("DATABASE_URL", "postgres://u:p@h/db")
    assert _database_url().startswith("postgresql+psycopg2://")
    monkeypatch.setenv("DATABASE_URL", "postgresql://u:p@h/db")
    assert _database_url().startswith("postgresql+psycopg2://")
