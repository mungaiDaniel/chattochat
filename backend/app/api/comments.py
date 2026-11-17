"""Comments on posts."""
from flask import Blueprint
from flask_jwt_extended import jwt_required

from ..extensions import db
from ..models import Comment, Post
from ..schemas import CommentSchema
from .helpers import current_user, get_or_404, ok, parse_body

bp = Blueprint("comments", __name__)


@bp.post("/comment/<int:post_id>")
@jwt_required()
def add_comment(post_id: int):
    post = get_or_404(Post, post_id, "Post")
    data = parse_body(CommentSchema())
    comment = Comment(post_id=post.id, user_id=current_user().id, body=data["body"].strip())
    db.session.add(comment)
    db.session.commit()
    return ok(comment.to_dict(), 201, message="Comment posted successfully")


@bp.get("/comments/<int:post_id>")
def list_comments(post_id: int):
    post = get_or_404(Post, post_id, "Post")
    return ok([c.to_dict() for c in post.comments])


@bp.get("/comment/<int:comment_id>")
def get_comment(comment_id: int):
    return ok(get_or_404(Comment, comment_id, "Comment").to_dict())
