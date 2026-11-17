"""SQLAlchemy models. Portable across PostgreSQL (production) and SQLite (dev/tests)."""
from datetime import datetime, timezone

from flask import current_app
from sqlalchemy import UniqueConstraint
from werkzeug.security import check_password_hash, generate_password_hash

from .extensions import db


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _iso(dt: datetime) -> str:
    """ISO-8601 in UTC. SQLite returns naive datetimes, PostgreSQL aware ones; normalise both."""
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.isoformat()


def media_url(path: str | None) -> str | None:
    """Turn a stored upload path into a root-relative URL ("/uploads/..."). Full URLs pass through."""
    if not path:
        return None
    if path.startswith(("http://", "https://")):
        return path
    return "/" + path.lstrip("/")


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    username = db.Column(db.String(50), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    user_role = db.Column(db.String(20), nullable=False, default="user")
    person_pic = db.Column(db.String(500))
    cover_pic = db.Column(db.String(500))
    date_created = db.Column(db.DateTime(timezone=True), nullable=False, default=_now)

    posts = db.relationship("Post", back_populates="author", cascade="all, delete-orphan")

    def set_password(self, password: str) -> None:
        method = current_app.config.get("PASSWORD_HASH_METHOD", "scrypt")
        self.password_hash = generate_password_hash(password, method=method)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)

    def to_public_dict(self) -> dict:
        """Fields safe to expose to any visitor (no email)."""
        return {
            "id": self.id,
            "name": self.name,
            "username": self.username,
            "user_role": self.user_role,
            "personPic": media_url(self.person_pic),
            "coverPic": media_url(self.cover_pic),
            "date_created": _iso(self.date_created),
        }

    def to_dict(self) -> dict:
        """Full representation, returned only to the account owner."""
        return {**self.to_public_dict(), "email": self.email}


class Post(db.Model):
    __tablename__ = "posts"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    body = db.Column(db.String(500), nullable=False)
    postpic = db.Column(db.String(500))
    likes = db.Column(db.Integer, nullable=False, default=0)
    date_created = db.Column(db.DateTime(timezone=True), nullable=False, default=_now, index=True)

    author = db.relationship("User", back_populates="posts")
    comments = db.relationship(
        "Comment", back_populates="post", cascade="all, delete-orphan", order_by="Comment.id"
    )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "user_id": self.user_id,
            "author": self.author.to_public_dict(),
            "body": self.body,
            "postpic": media_url(self.postpic),
            "likes": self.likes,
            "date_created": _iso(self.date_created),
            "comments": [c.to_dict() for c in self.comments],
        }


class Comment(db.Model):
    __tablename__ = "comments"

    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey("posts.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    body = db.Column(db.String(400), nullable=False)
    date_created = db.Column(db.DateTime(timezone=True), nullable=False, default=_now)

    post = db.relationship("Post", back_populates="comments")
    author = db.relationship("User")

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "post_id": self.post_id,
            "user_id": self.user_id,
            "author": self.author.to_public_dict(),
            "body": self.body,
            "date_created": _iso(self.date_created),
        }


class Follow(db.Model):
    __tablename__ = "follows"
    __table_args__ = (UniqueConstraint("follower_id", "followee_id", name="uq_follow_pair"),)

    id = db.Column(db.Integer, primary_key=True)
    follower_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    followee_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)

    followee = db.relationship("User", foreign_keys=[followee_id])

    def to_dict(self) -> dict:
        return {"id": self.id, "follower_id": self.follower_id, "followee_id": self.followee_id}
