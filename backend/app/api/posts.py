"""Posts: feed, create, read, edit, delete."""
from flask import Blueprint, request
from flask_jwt_extended import jwt_required
from sqlalchemy.orm import selectinload

from ..errors import ApiError
from ..extensions import db
from ..models import Comment, Post
from ..schemas import PostSchema, PostUpdateSchema
from ..uploads import save_image
from .helpers import current_user, get_or_404, ok, parse_body

bp = Blueprint("posts", __name__)

MAX_PAGE_SIZE = 100


def _post_query():
    return db.select(Post).options(
        selectinload(Post.author), selectinload(Post.comments).selectinload(Comment.author)
    )


def _page_args() -> tuple[int, int]:
    try:
        limit = int(request.args.get("limit", 50))
        offset = int(request.args.get("offset", 0))
    except ValueError:
        raise ApiError(400, "limit and offset must be integers")
    if limit < 1 or offset < 0:
        raise ApiError(400, "limit must be >= 1 and offset >= 0")
    return min(limit, MAX_PAGE_SIZE), offset


def _own_post(post_id: int) -> Post:
    post = get_or_404(Post, post_id, "Post")
    if post.user_id != current_user().id:
        raise ApiError(403, "You can only modify your own posts")
    return post


@bp.get("/post")
def list_posts():
    limit, offset = _page_args()
    posts = db.session.scalars(
        _post_query().order_by(Post.date_created.desc(), Post.id.desc()).limit(limit).offset(offset)
    ).all()
    return ok([p.to_dict() for p in posts])


@bp.post("/post")
@jwt_required()
def create_post():
    user = current_user()
    if request.files:
        # multipart/form-data: text in form fields, optional image in "photo"
        data = parse_body(PostSchema(), request.form.to_dict())
        postpic = save_image(request.files["photo"], "posts") if "photo" in request.files else None
        if "photo" in request.files and postpic is None:
            raise ApiError(400, "Invalid image. Allowed types: png, jpg, jpeg, gif, webp.")
    else:
        data = parse_body(PostSchema())
        postpic = data["postpic"]

    post = Post(user_id=user.id, body=data["body"].strip(), postpic=postpic or None)
    db.session.add(post)
    db.session.commit()
    return ok(post.to_dict(), 201, message="Posted successfully")


@bp.get("/post/<int:post_id>")
def get_post(post_id: int):
    post = db.session.scalar(_post_query().where(Post.id == post_id))
    if post is None:
        raise ApiError(404, "Post not found")
    return ok(post.to_dict())


@bp.put("/post/<int:post_id>")
@jwt_required()
def update_post(post_id: int):
    post = _own_post(post_id)
    post.body = parse_body(PostUpdateSchema())["body"].strip()
    db.session.commit()
    return ok(post.to_dict())


@bp.delete("/post/<int:post_id>")
@jwt_required()
def delete_post(post_id: int):
    post = _own_post(post_id)
    db.session.delete(post)
    db.session.commit()
    return "", 204


@bp.get("/mypost")
@jwt_required()
def my_posts():
    user = current_user()
    posts = db.session.scalars(
        _post_query().where(Post.user_id == user.id).order_by(Post.date_created.desc(), Post.id.desc())
    ).all()
    return ok([p.to_dict() for p in posts])
