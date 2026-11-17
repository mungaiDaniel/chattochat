"""Follow graph."""
from flask import Blueprint
from flask_jwt_extended import jwt_required

from ..errors import ApiError
from ..extensions import db
from ..models import Follow, User
from .helpers import current_user, get_or_404, ok

bp = Blueprint("follows", __name__)


def _target(user_id: int, me: User) -> User:
    target = get_or_404(User, user_id, "User")
    if target.id == me.id:
        raise ApiError(400, "You cannot follow yourself")
    return target


def _existing(me: User, target: User) -> Follow | None:
    return db.session.scalar(
        db.select(Follow).where(Follow.follower_id == me.id, Follow.followee_id == target.id)
    )


@bp.post("/follow/<int:user_id>")
@jwt_required()
def follow(user_id: int):
    me = current_user()
    target = _target(user_id, me)
    if _existing(me, target):
        raise ApiError(409, "You already follow this user")
    rel = Follow(follower_id=me.id, followee_id=target.id)
    db.session.add(rel)
    db.session.commit()
    return ok(rel.to_dict(), 201, message="Followed successfully")


@bp.post("/unfollow/<int:user_id>")
@jwt_required()
def unfollow(user_id: int):
    me = current_user()
    target = _target(user_id, me)
    rel = _existing(me, target)
    if rel is None:
        raise ApiError(404, "You are not following this user")
    db.session.delete(rel)
    db.session.commit()
    return ok(message="Unfollowed successfully")


@bp.get("/following")
@jwt_required()
def following():
    me = current_user()
    users = db.session.scalars(
        db.select(User)
        .join(Follow, Follow.followee_id == User.id)
        .where(Follow.follower_id == me.id)
        .order_by(User.id)
    ).all()
    return ok([u.to_public_dict() for u in users])
