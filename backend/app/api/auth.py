"""Registration and login."""
from flask import Blueprint
from flask_jwt_extended import create_access_token
from sqlalchemy import func

from ..errors import ApiError
from ..extensions import db, limiter
from ..models import User
from ..schemas import LoginSchema, RegisterSchema
from .helpers import ok, parse_body

bp = Blueprint("auth", __name__)

_dummy_user: User | None = None


def _timing_dummy() -> User:
    """A throwaway user whose hash is checked when the account doesn't exist,
    so response time doesn't reveal which usernames are registered."""
    global _dummy_user
    if _dummy_user is None:
        _dummy_user = User(password_hash="")
        _dummy_user.set_password("not-a-real-password")
    return _dummy_user


@bp.post("/register")
@limiter.limit("10 per minute")
def register():
    data = parse_body(RegisterSchema())
    email = data["email"].lower()

    taken = db.session.scalar(
        db.select(User).where(
            (func.lower(User.username) == data["username"].lower()) | (User.email == email)
        )
    )
    if taken:
        raise ApiError(409, "Username or email is already registered")

    # The role is never taken from the client: new accounts are always plain users.
    user = User(name=data["name"].strip(), username=data["username"], email=email, user_role="user")
    user.set_password(data["password"])
    db.session.add(user)
    db.session.commit()
    return ok(user.to_dict(), 201)


@bp.post("/login")
@limiter.limit("5 per minute")
def login():
    data = parse_body(LoginSchema())
    identifier = data["username"]

    user = db.session.scalar(
        db.select(User).where(
            (func.lower(User.username) == identifier.lower()) | (User.email == identifier.lower())
        )
    )
    # Identical error for "no such user" and "wrong password" prevents account enumeration.
    if not (user or _timing_dummy()).check_password(data["password"]) or user is None:
        raise ApiError(401, "Invalid username or password")

    token = create_access_token(identity=str(user.id), additional_claims={"role": user.user_role})
    return ok(user.to_dict(), token=token, user_role=user.user_role, id=user.id)
