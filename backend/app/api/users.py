"""User directory, profile management, photo upload and the (simulated) premium upgrade."""
from flask import Blueprint, request
from flask_jwt_extended import jwt_required

from ..errors import ApiError
from ..extensions import db
from ..models import User
from ..schemas import ProfileSchema, RoleSchema
from ..uploads import save_image
from .helpers import current_user, get_or_404, ok, parse_body

bp = Blueprint("users", __name__)


@bp.get("/user")
def list_users():
    users = db.session.scalars(db.select(User).order_by(User.id)).all()
    return ok([u.to_public_dict() for u in users])


# Declared before /user/<int:id>; Flask matches the static segment first regardless.
@bp.get("/user/me")
@jwt_required()
def me():
    return ok(current_user().to_dict())


@bp.get("/user/<int:user_id>")
def get_user(user_id: int):
    return ok(get_or_404(User, user_id, "User").to_public_dict())


@bp.put("/user/profile")
@jwt_required()
def update_profile():
    data = parse_body(ProfileSchema())
    user = current_user()
    if "personPic" in data:
        user.person_pic = data["personPic"]
    if "coverPic" in data:
        user.cover_pic = data["coverPic"]
    db.session.commit()
    return ok(user.to_dict(), message="Profile updated successfully")


@bp.put("/premium")
@jwt_required()
def change_role():
    """Simulated plan change. A real deployment would gate this behind a payment provider webhook."""
    data = parse_body(RoleSchema())
    user = current_user()
    user.user_role = data["user_role"]
    db.session.commit()
    return ok({"user_role": user.user_role})


@bp.post("/upload-photo")
@jwt_required()
def upload_photo():
    file = request.files.get("photo")
    if file is None or not file.filename:
        raise ApiError(400, "No file provided. Send it as multipart form field 'photo'.")

    path = save_image(file, "photos")
    if path is None:
        raise ApiError(400, "Invalid image. Allowed types: png, jpg, jpeg, gif, webp.")
    return ok(
        message="Photo uploaded successfully",
        filename=path.rsplit("/", 1)[-1],
        file_path=path,
        photo_url="/" + path,
    )
