"""Request validation schemas (marshmallow). Unknown fields are silently dropped."""
from marshmallow import EXCLUDE, Schema, ValidationError, fields, validate, validates_schema


def _not_blank(value: str) -> None:
    if not value.strip():
        raise ValidationError("Must not be blank.")


class _Base(Schema):
    class Meta:
        unknown = EXCLUDE


class RegisterSchema(_Base):
    name = fields.Str(required=True, validate=[validate.Length(min=1, max=100), _not_blank])
    username = fields.Str(
        required=True,
        validate=validate.Regexp(
            r"^[A-Za-z0-9_.-]{3,50}$",
            error="3-50 characters: letters, digits, underscore, dot or hyphen.",
        ),
    )
    email = fields.Email(required=True, validate=validate.Length(max=120))
    password = fields.Str(required=True, validate=validate.Length(min=8, max=128), load_only=True)


class LoginSchema(_Base):
    # "username" may also contain the account's email address.
    username = fields.Str(required=True, validate=validate.Length(min=1, max=120))
    password = fields.Str(required=True, validate=validate.Length(min=1, max=128))


class PostSchema(_Base):
    body = fields.Str(required=True, validate=[validate.Length(min=1, max=500), _not_blank])
    postpic = fields.Str(load_default=None, allow_none=True, validate=validate.Length(max=500))


class PostUpdateSchema(_Base):
    body = fields.Str(required=True, validate=[validate.Length(min=1, max=500), _not_blank])


class CommentSchema(_Base):
    body = fields.Str(required=True, validate=[validate.Length(min=1, max=400), _not_blank])


def _image_ref(value: str) -> None:
    if not (value.startswith(("http://", "https://")) or value.lstrip("/").startswith("uploads/")):
        raise ValidationError("Must be an uploaded file path or an http(s) URL.")


class ProfileSchema(_Base):
    personPic = fields.Str(validate=[validate.Length(max=500), _image_ref])
    coverPic = fields.Str(validate=[validate.Length(max=500), _image_ref])

    @validates_schema
    def at_least_one(self, data, **kwargs):
        if not data:
            raise ValidationError("Provide at least one of: personPic, coverPic.")


class RoleSchema(_Base):
    user_role = fields.Str(required=True, validate=validate.OneOf(["user", "premium"]))
