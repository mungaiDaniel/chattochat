"""HTTP API blueprints, all mounted under ``/api/v1``."""
from . import auth, comments, follows, posts, users

API_PREFIX = "/api/v1"
BLUEPRINTS = (auth.bp, users.bp, posts.bp, comments.bp, follows.bp)
