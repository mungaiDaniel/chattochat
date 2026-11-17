import io

import pytest

from app import create_app
from app.extensions import db

# Smallest valid files for each supported format (only the signature matters to the validator).
PNG_BYTES = b"\x89PNG\r\n\x1a\n" + b"\x00" * 32
JPEG_BYTES = b"\xff\xd8\xff\xe0" + b"\x00" * 32
GIF_BYTES = b"GIF89a" + b"\x00" * 32
WEBP_BYTES = b"RIFF\x00\x00\x00\x00WEBP" + b"\x00" * 32


@pytest.fixture()
def app(tmp_path):
    app = create_app("testing")
    app.config["UPLOAD_FOLDER"] = str(tmp_path / "uploads")
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture()
def client(app):
    return app.test_client()


USER = {
    "name": "Test User",
    "username": "testuser",
    "email": "test.user@example.com",
    "password": "correct-horse-battery",
}
OTHER = {
    "name": "Other Person",
    "username": "otherperson",
    "email": "other.person@example.com",
    "password": "another-long-password",
}


@pytest.fixture()
def register(client):
    """Register an account and return the created user's dict."""

    def _register(payload=USER):
        resp = client.post("/api/v1/register", json=payload)
        assert resp.status_code == 201, resp.get_json()
        return resp.get_json()["data"]

    return _register


@pytest.fixture()
def login(client):
    """Log in and return ``(headers, user_id)`` for authenticated requests."""

    def _login(payload=USER):
        resp = client.post(
            "/api/v1/login", json={"username": payload["username"], "password": payload["password"]}
        )
        assert resp.status_code == 200, resp.get_json()
        body = resp.get_json()
        return {"Authorization": f"Bearer {body['token']}"}, body["id"]

    return _login


@pytest.fixture()
def auth(register, login):
    """Headers for a freshly registered + logged-in default user."""
    register()
    headers, _ = login()
    return headers


@pytest.fixture()
def other_auth(register, login):
    register(OTHER)
    headers, _ = login(OTHER)
    return headers


@pytest.fixture()
def make_post(client):
    def _make_post(headers, body="Hello from a test post"):
        resp = client.post("/api/v1/post", json={"body": body}, headers=headers)
        assert resp.status_code == 201, resp.get_json()
        return resp.get_json()["data"]

    return _make_post


@pytest.fixture()
def image_file():
    def _image(name="pic.png", content=PNG_BYTES):
        return io.BytesIO(content), name

    return _image
