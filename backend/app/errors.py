"""Uniform JSON error responses.

Every error returned by the API has the shape::

    {"status": <http code>, "message": "<human readable>", "errors": {...optional...}}
"""
import logging

from flask import Flask, jsonify
from marshmallow import ValidationError
from sqlalchemy.exc import IntegrityError
from werkzeug.exceptions import HTTPException

from .extensions import db, jwt

log = logging.getLogger(__name__)


class ApiError(Exception):
    """Raise anywhere in a request to short-circuit with a JSON error."""

    def __init__(self, status: int, message: str, errors: dict | None = None):
        super().__init__(message)
        self.status = status
        self.message = message
        self.errors = errors


def error_response(status: int, message: str, errors: dict | None = None):
    body = {"status": status, "message": message}
    if errors:
        body["errors"] = errors
    return jsonify(body), status


def register_error_handlers(app: Flask) -> None:
    @app.errorhandler(ApiError)
    def handle_api_error(err: ApiError):
        return error_response(err.status, err.message, err.errors)

    @app.errorhandler(ValidationError)
    def handle_validation_error(err: ValidationError):
        return error_response(422, "Validation failed", err.normalized_messages())

    @app.errorhandler(IntegrityError)
    def handle_integrity_error(err: IntegrityError):
        db.session.rollback()
        log.warning("Integrity error: %s", err.orig)
        return error_response(409, "Resource already exists or conflicts with existing data")

    @app.errorhandler(HTTPException)
    def handle_http_exception(err: HTTPException):
        return error_response(err.code or 500, err.description or err.name)

    @app.errorhandler(Exception)
    def handle_unexpected(err: Exception):
        db.session.rollback()
        log.exception("Unhandled error")
        return error_response(500, "Internal server error")

    # JWT failures -> consistent 401 payloads
    @jwt.unauthorized_loader
    def missing_token(reason: str):
        return error_response(401, "Authentication required")

    @jwt.invalid_token_loader
    def invalid_token(reason: str):
        return error_response(401, "Invalid token")

    @jwt.expired_token_loader
    def expired_token(header, payload):
        return error_response(401, "Token has expired")
