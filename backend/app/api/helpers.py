"""Small helpers shared by the API blueprints."""
from flask import request
from flask_jwt_extended import get_jwt_identity
from marshmallow import Schema

from ..errors import ApiError
from ..extensions import db
from ..models import User


def parse_body(schema: Schema, data: dict | None = None) -> dict:
    """Validate the JSON body (or the given dict) against ``schema``.

    Raises a 400 if the body is not a JSON object and a 422 (via marshmallow) if fields are invalid.
    """
    if data is None:
        data = request.get_json(silent=True)
    if not isinstance(data, dict):
        raise ApiError(400, "Request body must be a JSON object")
    return schema.load(data)


def current_user() -> User:
    """The authenticated user. Call only inside a ``@jwt_required()`` view."""
    user = db.session.get(User, int(get_jwt_identity()))
    if user is None:
        # Valid token for an account that no longer exists.
        raise ApiError(401, "Account no longer exists")
    return user


def get_or_404(model, pk: int, label: str):
    obj = db.session.get(model, pk)
    if obj is None:
        raise ApiError(404, f"{label} not found")
    return obj


def ok(payload: dict | None = None, status: int = 200, **extra):
    """Standard success envelope: ``{"status": 200, "data": ...}``."""
    body = {"status": status}
    if payload is not None:
        body["data"] = payload
    body.update(extra)
    return body, status
