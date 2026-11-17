import time

import pytest
from flask_jwt_extended import create_access_token

from conftest import OTHER, USER


class TestRegister:
    def test_register_success_hides_password_and_forces_user_role(self, client):
        resp = client.post("/api/v1/register", json={**USER, "user_role": "premium"})
        assert resp.status_code == 201
        data = resp.get_json()["data"]
        assert data["username"] == USER["username"]
        assert data["email"] == USER["email"]
        assert data["user_role"] == "user"  # client-supplied role is ignored
        assert "password" not in data and "password_hash" not in data

    def test_email_is_normalised_to_lowercase(self, client):
        resp = client.post("/api/v1/register", json={**USER, "email": "Test.User@Example.COM"})
        assert resp.get_json()["data"]["email"] == "test.user@example.com"

    def test_duplicate_username_conflicts_case_insensitively(self, client, register):
        register()
        resp = client.post(
            "/api/v1/register", json={**OTHER, "username": USER["username"].upper()}
        )
        assert resp.status_code == 409

    def test_duplicate_email_conflicts(self, client, register):
        register()
        resp = client.post("/api/v1/register", json={**OTHER, "email": USER["email"]})
        assert resp.status_code == 409

    @pytest.mark.parametrize(
        "field,value",
        [
            ("email", "not-an-email"),
            ("password", "short"),
            ("username", "a b"),
            ("username", "ab"),
            ("name", "   "),
        ],
    )
    def test_invalid_fields_return_422_with_details(self, client, field, value):
        resp = client.post("/api/v1/register", json={**USER, field: value})
        assert resp.status_code == 422
        body = resp.get_json()
        assert body["status"] == 422
        assert field in body["errors"]

    def test_missing_fields_return_422(self, client):
        resp = client.post("/api/v1/register", json={"username": "someone"})
        assert resp.status_code == 422
        assert {"name", "email", "password"} <= set(resp.get_json()["errors"])

    def test_non_json_body_returns_400(self, client):
        resp = client.post("/api/v1/register", data="plain text", content_type="text/plain")
        assert resp.status_code == 400

    def test_json_array_body_returns_400(self, client):
        assert client.post("/api/v1/register", json=[1, 2]).status_code == 400

    def test_sql_injection_attempt_is_just_a_string(self, client, register):
        register()
        resp = client.post(
            "/api/v1/login", json={"username": "' OR '1'='1", "password": "' OR '1'='1"}
        )
        assert resp.status_code == 401


class TestLogin:
    def test_login_returns_token_and_user(self, client, register):
        register()
        resp = client.post(
            "/api/v1/login", json={"username": USER["username"], "password": USER["password"]}
        )
        assert resp.status_code == 200
        body = resp.get_json()
        assert body["token"]
        assert body["user_role"] == "user"
        assert body["data"]["email"] == USER["email"]

    def test_login_with_email_works(self, client, register):
        register()
        resp = client.post(
            "/api/v1/login", json={"username": USER["email"], "password": USER["password"]}
        )
        assert resp.status_code == 200

    def test_wrong_password_and_unknown_user_are_indistinguishable(self, client, register):
        register()
        wrong = client.post("/api/v1/login", json={"username": USER["username"], "password": "nope"})
        unknown = client.post("/api/v1/login", json={"username": "ghost", "password": "nope"})
        assert wrong.status_code == unknown.status_code == 401
        assert wrong.get_json()["message"] == unknown.get_json()["message"]

    def test_missing_password_returns_422(self, client):
        assert client.post("/api/v1/login", json={"username": "x"}).status_code == 422

    def test_passwords_are_stored_hashed(self, app, register):
        from app.extensions import db
        from app.models import User

        register()
        user = db.session.scalar(db.select(User))
        assert user.password_hash != USER["password"]
        assert user.check_password(USER["password"])


class TestJwt:
    def test_protected_route_requires_token(self, client):
        resp = client.get("/api/v1/mypost")
        assert resp.status_code == 401
        assert resp.get_json()["message"] == "Authentication required"

    def test_garbage_token_rejected(self, client):
        resp = client.get("/api/v1/mypost", headers={"Authorization": "Bearer not.a.jwt"})
        assert resp.status_code == 401

    def test_expired_token_rejected(self, app, client, register):
        user = register()
        from datetime import timedelta

        token = create_access_token(identity=str(user["id"]), expires_delta=timedelta(seconds=-1))
        resp = client.get("/api/v1/mypost", headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 401
        assert resp.get_json()["message"] == "Token has expired"

    def test_token_for_deleted_account_rejected(self, app, client):
        token = create_access_token(identity="9999")
        resp = client.get("/api/v1/user/me", headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 401

    def test_token_signed_with_wrong_key_rejected(self, app, client, register):
        import jwt as pyjwt

        user = register()
        forged = pyjwt.encode(
            {"sub": str(user["id"]), "exp": int(time.time()) + 600, "type": "access",
             "fresh": False, "jti": "x"},
            "x" * 40,
            algorithm="HS256",
        )
        resp = client.get("/api/v1/mypost", headers={"Authorization": f"Bearer {forged}"})
        assert resp.status_code == 401
