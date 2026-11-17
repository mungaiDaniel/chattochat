"""WSGI entry point: ``gunicorn wsgi:app`` or ``flask --app wsgi run``."""
from dotenv import load_dotenv

load_dotenv()

from app import create_app  # noqa: E402  (must come after load_dotenv)

app = create_app()
