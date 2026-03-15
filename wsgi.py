"""
manage.py

Compatibility entrypoint for Flask CLI.

Phase 1: we make `wsgi.py` the single authoritative app entrypoint.
This file remains so existing workflows like `flask --app manage.py ...`
continue to work, but all CLI commands are registered by the app factory.
"""

from app import create_app

app = create_app()